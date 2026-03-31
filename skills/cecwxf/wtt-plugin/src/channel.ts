/**
 * WTT Channel Plugin for OpenClaw.
 *
 * Scope of this module (P0/P1 foundation):
 * - Register WTT as a first-class channel plugin
 * - Manage per-account WS clients
 * - Provide outbound text/media delivery through WTT publish/p2p
 *
 * Command parity status:
 * - Core @wtt topic/message commands routed in src/commands/* (P2 first batch)
 * - task/pipeline/delegate command scaffolding available via HTTP API in src/commands/*
 */

import type {
  WTTAccountConfig,
  ResolvedWTTAccount,
  WsNewMessage,
  WsTaskStatus,
  WsMessagePayload,
} from "./types.js";
import type { WTTCommandProcessResult } from "./commands/router.js";
import type {
  WTTCommandAccountContext,
  WTTCommandRuntimeHooks,
  WTTTaskInferenceRuntimeRequest,
  WTTTaskInferenceUsage,
  WTTSessionRuntimeMetrics,
} from "./commands/types.js";
import { createWTTCommandRouter } from "./commands/router.js";
import { normalizeAccountContext } from "./commands/account.js";
import { executeTaskRunById } from "./commands/task.js";
import { createTaskStatusEventHandler } from "./runtime/task-status-handler.js";
import { WTTCloudClient } from "./ws-client.js";
import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import os from "node:os";
import { dirname, join as joinPath } from "node:path";
import { randomBytes } from "node:crypto";
import { pathToFileURL } from "node:url";

const DEFAULT_ACCOUNT_ID = "default";
const DEFAULT_CLOUD_URL = "https://www.waxbyte.com";
const CHANNEL_ID = "wtt";
const DEFAULT_INBOUND_POLL_INTERVAL_MS = 0;
const DEFAULT_INBOUND_POLL_LIMIT = 20;
const DEFAULT_INBOUND_DEDUP_WINDOW_MS = 5 * 60_000;
const DEFAULT_INBOUND_DEDUP_MAX_ENTRIES = 2000;
const DEFAULT_TASK_RECOVERY_INTERVAL_MS = 60_000;
const DEFAULT_TASK_RECOVERY_LOOKBACK_MS = 6 * 60 * 60_000;
const DEFAULT_SLASH_COMPAT_ENABLED = false;
const DEFAULT_SLASH_COMPAT_WTT_PREFIX_ONLY = true;
const DEFAULT_SLASH_BYPASS_MENTION_GATE = false;
const DEFAULT_NATURAL_BRIDGE_MIN_DOING_MS = 2500;

type OpenClawConfig = {
  session?: {
    store?: string;
  };
  channels?: {
    wtt?: {
      accounts?: Record<string, WTTAccountConfig>;
    } & WTTAccountConfig;
  };
};

type HookFn = (ctx: {
  tool: string;
  args: Record<string, unknown>;
  result?: unknown;
}) => void | Promise<void>;

type ChannelLogSink = {
  info?: (msg: string) => void;
  warn?: (msg: string) => void;
  error?: (msg: string) => void;
  debug?: (msg: string) => void;
};

type MsgContextLike = Record<string, unknown>;

type ChannelRuntimeLike = {
  routing: {
    resolveAgentRoute: (params: {
      cfg: OpenClawConfig;
      channel: string;
      accountId?: string | null;
      peer?: { kind: "direct" | "group" | "channel"; id: string } | null;
    }) => { agentId: string; accountId: string; sessionKey: string };
  };
  session: {
    resolveStorePath: (storePath: string | undefined, params: { agentId: string }) => string;
    readSessionUpdatedAt: (params: { storePath: string; sessionKey: string }) => string | number | null | undefined;
    recordInboundSession: (params: {
      storePath: string;
      sessionKey: string;
      ctx: MsgContextLike;
      updateLastRoute?: {
        sessionKey: string;
        channel: string;
        to: string;
        accountId?: string;
      };
      onRecordError: (err: unknown) => void;
    }) => Promise<void>;
  };
  reply: {
    resolveEnvelopeFormatOptions: (cfg: OpenClawConfig) => unknown;
    formatAgentEnvelope: (params: {
      channel: string;
      from: string;
      timestamp: string;
      previousTimestamp?: string | number | null;
      envelope?: unknown;
      body: string;
    }) => string;
    finalizeInboundContext: (ctx: MsgContextLike) => MsgContextLike;
    dispatchReplyWithBufferedBlockDispatcher: (params: {
      ctx: MsgContextLike;
      cfg: OpenClawConfig;
      dispatcherOptions: {
        deliver: (payload: Record<string, unknown>) => Promise<void>;
        onError?: (err: unknown, info: { kind: string }) => void;
      };
      replyOptions?: Record<string, unknown>;
    }) => Promise<unknown>;
  };
};

type GatewayStartContext = {
  cfg: OpenClawConfig;
  accountId: string;
  account: ResolvedWTTAccount;
  abortSignal: AbortSignal;
  log?: ChannelLogSink;
  channelRuntime?: ChannelRuntimeLike;
};

const hooks: { before: HookFn[]; after: HookFn[] } = { before: [], after: [] };
const clients = new Map<string, WTTCloudClient>();
const topicTypeCache = new Map<string, string>();
const DEFAULT_P2P_E2E_ENABLED = true;

function registerHook(phase: "before_tool_call" | "after_tool_call", fn: HookFn): void {
  if (phase === "before_tool_call") hooks.before.push(fn);
  else hooks.after.push(fn);
}

async function runHooks(phase: "before" | "after", ctx: Parameters<HookFn>[0]): Promise<void> {
  for (const fn of hooks[phase]) await fn(ctx);
}

function listAccountIds(cfg: OpenClawConfig): string[] {
  const section = cfg.channels?.wtt;
  if (!section) return [];

  const ids = Object.keys(section.accounts ?? {});
  if (ids.length > 0) return ids;

  // Backward compatibility with flat single-account config under channels.wtt
  if (section.agentId || section.token || section.cloudUrl || section.name) return [DEFAULT_ACCOUNT_ID];
  return [];
}

function resolveRawAccountConfig(cfg: OpenClawConfig, accountId?: string): WTTAccountConfig {
  const section = cfg.channels?.wtt ?? {};
  const id = accountId ?? DEFAULT_ACCOUNT_ID;

  if (section.accounts?.[id]) return section.accounts[id];
  if (id === DEFAULT_ACCOUNT_ID) {
    const { accounts: _accounts, ...flat } = section;
    return flat;
  }
  return {};
}

function resolveAccount(cfg: OpenClawConfig, accountId?: string): ResolvedWTTAccount {
  const id = accountId ?? DEFAULT_ACCOUNT_ID;
  const raw = resolveRawAccountConfig(cfg, id);
  const enabled = raw.enabled !== false;
  const configured = Boolean(raw.agentId?.trim() && raw.token?.trim());

  return {
    accountId: id,
    name: raw.name ?? id,
    enabled,
    configured,
    cloudUrl: raw.cloudUrl ?? DEFAULT_CLOUD_URL,
    agentId: raw.agentId ?? "",
    token: raw.token ?? "",
    config: raw,
  };
}

function openclawConfigPath(): string {
  const fromEnv = process.env.OPENCLAW_CONFIG_PATH?.trim();
  if (fromEnv) return fromEnv;
  return joinPath(os.homedir(), ".openclaw", "openclaw.json");
}

function generateE2EPassword(): string {
  return randomBytes(24).toString("base64url");
}

async function ensureAccountE2EPassword(accountId: string, account: ResolvedWTTAccount, log: (level: "debug" | "info" | "warn" | "error", msg: string, data?: unknown) => void): Promise<void> {
  if (account.config.e2ePassword?.trim()) return;

  const password = generateE2EPassword();
  const configPath = openclawConfigPath();

  try {
    let cfgRaw: Record<string, unknown> = {};
    try {
      const text = await readFile(configPath, "utf8");
      cfgRaw = JSON.parse(text) as Record<string, unknown>;
    } catch (err) {
      const code = (err as NodeJS.ErrnoException | undefined)?.code;
      if (code !== "ENOENT") throw err;
    }

    const channels = ((cfgRaw.channels as Record<string, unknown> | undefined) ?? {});
    const wtt = ((channels.wtt as Record<string, unknown> | undefined) ?? {});
    const accounts = ((wtt.accounts as Record<string, unknown> | undefined) ?? {});

    const accountKey = accountId || DEFAULT_ACCOUNT_ID;
    const currentAccount = ((accounts[accountKey] as Record<string, unknown> | undefined) ?? {});

    const existing = typeof currentAccount.e2ePassword === "string" ? currentAccount.e2ePassword.trim() : "";
    if (existing) {
      account.config.e2ePassword = existing;
      return;
    }

    const mergedAccount = {
      ...currentAccount,
      e2ePassword: password,
    };

    const next = {
      ...cfgRaw,
      channels: {
        ...channels,
        wtt: {
          ...wtt,
          accounts: {
            ...accounts,
            [accountKey]: mergedAccount,
          },
        },
      },
    };

    await mkdir(dirname(configPath), { recursive: true });
    const tempPath = `${configPath}.tmp-${Date.now()}`;
    await writeFile(tempPath, `${JSON.stringify(next, null, 2)}\n`, "utf8");
    await rename(tempPath, configPath);

    account.config.e2ePassword = password;
    log("info", `[${accountId}] auto-generated e2ePassword and persisted to openclaw.json`);
  } catch (err) {
    log("warn", `[${accountId}] failed to auto-generate e2ePassword`, err);
  }
}

function rememberTopicType(topicId: string | undefined, topicType: string | undefined): void {
  const id = (topicId ?? "").trim();
  if (!id) return;
  const type = (topicType ?? "").trim().toLowerCase();
  if (!type) return;
  topicTypeCache.set(id, type);
  while (topicTypeCache.size > 5000) {
    const oldest = topicTypeCache.keys().next().value;
    if (!oldest) break;
    topicTypeCache.delete(oldest);
  }
}

function isP2PTopicId(topicId: string): boolean {
  const type = topicTypeCache.get(topicId.trim());
  return type === "p2p";
}

function isP2PE2EEnabled(account: ResolvedWTTAccount): boolean {
  const raw = account.config.p2pE2EEnabled;
  return raw === undefined ? DEFAULT_P2P_E2E_ENABLED : raw !== false;
}

function getClient(accountId: string): WTTCloudClient | undefined {
  return clients.get(accountId);
}

function hasMeaningfulAccountConfig(raw: WTTAccountConfig): boolean {
  return Boolean(raw.agentId || raw.token || raw.cloudUrl || raw.name || raw.enabled !== undefined);
}

function detectAccountSource(cfg: OpenClawConfig | undefined, accountId: string): string {
  const section = cfg?.channels?.wtt;
  if (!section) return "runtime";
  if (section.accounts?.[accountId]) return `channels.wtt.accounts.${accountId}`;
  if (accountId === DEFAULT_ACCOUNT_ID) {
    const { accounts: _accounts, ...flat } = section;
    if (hasMeaningfulAccountConfig(flat)) return "channels.wtt";
  }
  return "runtime";
}

function resolveCommandAccountContext(accountId: string, cfg?: OpenClawConfig): WTTCommandAccountContext | undefined {
  if (cfg?.channels?.wtt) {
    const account = resolveAccount(cfg, accountId);
    return {
      accountId: account.accountId,
      name: account.name,
      source: detectAccountSource(cfg, accountId),
      cloudUrl: account.cloudUrl,
      agentId: account.agentId,
      token: account.token,
      enabled: account.enabled,
      configured: account.configured,
    };
  }

  const client = getClient(accountId);
  if (!client) return undefined;

  const runtime = client.getAccount();
  return {
    accountId: runtime.accountId,
    name: runtime.name,
    source: "runtime.client",
    cloudUrl: runtime.cloudUrl,
    agentId: runtime.agentId,
    token: runtime.token,
    enabled: runtime.enabled,
    configured: runtime.configured,
  };
}

const commandRouter = createWTTCommandRouter({
  getClient,
  getAccount: (accountId) => resolveCommandAccountContext(accountId),
  defaultAccountId: DEFAULT_ACCOUNT_ID,
});

function extractDispatchText(payload: unknown): string {
  if (!payload || typeof payload !== "object") return "";
  const data = payload as Record<string, unknown>;

  if (typeof data.text === "string" && data.text.trim()) {
    return data.text.trim();
  }

  const lines: string[] = [];
  const blocks = Array.isArray(data.blocks) ? data.blocks : [];
  for (const block of blocks) {
    if (!block || typeof block !== "object") continue;
    const piece = (block as Record<string, unknown>).text;
    if (typeof piece === "string" && piece.trim()) lines.push(piece.trim());
  }

  if (lines.length > 0) return lines.join("\n\n");
  return "";
}

function toNumberOrZero(raw: unknown): number {
  const n = Number(raw);
  if (!Number.isFinite(n) || n < 0) return 0;
  return Math.floor(n);
}

function toTimestampMs(raw: unknown): number | undefined {
  if (typeof raw === "number" && Number.isFinite(raw)) {
    if (raw > 1_000_000_000_000) return Math.floor(raw);
    if (raw > 1_000_000_000) return Math.floor(raw * 1000);
    return undefined;
  }

  if (typeof raw === "string" && raw.trim()) {
    const parsed = Date.parse(raw);
    if (Number.isFinite(parsed)) return parsed;
  }

  return undefined;
}

async function collectSessionUsageDelta(params: {
  storePath: string;
  sessionKey: string;
  sinceMs: number;
  untilMs?: number;
}): Promise<WTTTaskInferenceUsage | undefined> {
  const filePath = joinPath(params.storePath, `${params.sessionKey}.jsonl`);

  let content: string;
  try {
    content = await readFile(filePath, "utf8");
  } catch {
    return undefined;
  }

  const lines = content.split("\n");
  if (lines.length === 0) return undefined;

  const untilMs = Number.isFinite(params.untilMs) ? (params.untilMs as number) : Date.now();

  let promptTokens = 0;
  let completionTokens = 0;
  let cacheReadTokens = 0;
  let cacheWriteTokens = 0;
  let totalTokens = 0;
  let matched = 0;
  let provider: string | undefined;
  let model: string | undefined;

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    let entry: Record<string, unknown> | undefined;
    try {
      const parsed = JSON.parse(trimmed) as unknown;
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) continue;
      entry = parsed as Record<string, unknown>;
    } catch {
      continue;
    }

    if (entry.type !== "message") continue;

    const message = asRecord(entry.message);
    if (!message || message.role !== "assistant") continue;

    const ts = toTimestampMs(entry.timestamp ?? message.timestamp);
    if (typeof ts !== "number") continue;
    if (ts < params.sinceMs || ts > untilMs + 2_000) continue;

    const usage = asRecord(message.usage);
    if (!usage) continue;

    matched += 1;
    const input = toNumberOrZero(usage.input);
    const output = toNumberOrZero(usage.output);
    const cacheRead = toNumberOrZero(usage.cacheRead);
    const cacheWrite = toNumberOrZero(usage.cacheWrite);
    const total = toNumberOrZero(usage.totalTokens);

    promptTokens += input;
    completionTokens += output;
    cacheReadTokens += cacheRead;
    cacheWriteTokens += cacheWrite;
    totalTokens += total > 0 ? total : (input + output + cacheRead + cacheWrite);

    const msgProvider = typeof message.provider === "string" ? message.provider.trim() : "";
    const msgModel = typeof message.model === "string" ? message.model.trim() : "";
    if (msgProvider) provider = msgProvider;
    if (msgModel) model = msgModel;
  }

  if (matched <= 0) return undefined;

  return {
    promptTokens,
    completionTokens,
    cacheReadTokens,
    cacheWriteTokens,
    totalTokens,
    source: "openclaw_session_usage_delta",
    provider,
    model,
  };
}

type OpenClawQueueDepthReader = (key: string) => number;

let openClawQueueDepthReaderPromise: Promise<OpenClawQueueDepthReader | null> | null = null;

async function loadOpenClawQueueDepthReader(): Promise<OpenClawQueueDepthReader | null> {
  if (openClawQueueDepthReaderPromise) return openClawQueueDepthReaderPromise;

  openClawQueueDepthReaderPromise = (async () => {
    try {
      const require = createRequire(import.meta.url);
      const sdkEntry = require.resolve("openclaw/plugin-sdk");
      const enqueuePath = joinPath(dirname(sdkEntry), "auto-reply/reply/queue/enqueue.js");
      const mod = await import(pathToFileURL(enqueuePath).href) as unknown as {
        getFollowupQueueDepth?: (key: string) => number;
      };

      if (typeof mod.getFollowupQueueDepth === "function") {
        return mod.getFollowupQueueDepth;
      }
    } catch {
      // best-effort only
    }

    return null;
  })();

  return openClawQueueDepthReaderPromise;
}

async function resolveOpenClawQueueDepth(sessionKey: string): Promise<number | undefined> {
  if (!sessionKey) return undefined;

  try {
    const reader = await loadOpenClawQueueDepthReader();
    if (!reader) return undefined;
    const raw = reader(sessionKey);
    if (!Number.isFinite(raw)) return undefined;
    return Math.max(0, Math.floor(raw));
  } catch {
    return undefined;
  }
}

async function resolveOpenClawQueueModeFromStore(storePath: string, sessionKey: string): Promise<string | undefined> {
  if (!storePath || !sessionKey) return undefined;

  try {
    const raw = await readFile(storePath, "utf8");
    const parsed = JSON.parse(raw) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return undefined;

    const entry = (parsed as Record<string, unknown>)[sessionKey];
    if (!entry || typeof entry !== "object" || Array.isArray(entry)) return undefined;

    const mode = (entry as Record<string, unknown>).queueMode;
    return typeof mode === "string" && mode.trim() ? mode.trim() : undefined;
  } catch {
    return undefined;
  }
}

function createTaskInferenceRuntimeHooks(params: {
  cfg: OpenClawConfig;
  accountId: string;
  account?: WTTCommandAccountContext;
  channelRuntime?: ChannelRuntimeLike;
  typingSignal?: (args: { topicId: string; state: "start" | "stop"; ttlMs?: number }) => Promise<void>;
}): WTTCommandRuntimeHooks | undefined {
  const runtime = params.channelRuntime;
  if (!runtime) return undefined;

  return {
    getSessionRuntimeMetrics: async (request): Promise<WTTSessionRuntimeMetrics | undefined> => {
      const topicId = request.topicId?.trim();
      if (!topicId || topicId === "-") return undefined;

      const route = runtime.routing.resolveAgentRoute({
        cfg: params.cfg,
        channel: CHANNEL_ID,
        accountId: params.accountId,
        peer: { kind: "group", id: topicId },
      });

      const storePath = runtime.session.resolveStorePath(params.cfg.session?.store, {
        agentId: route.agentId,
      });

      const [queueDepth, queueMode] = await Promise.all([
        resolveOpenClawQueueDepth(route.sessionKey),
        resolveOpenClawQueueModeFromStore(storePath, route.sessionKey),
      ]);

      return {
        source: (typeof queueDepth === "number" || Boolean(queueMode)) ? "openclaw" : "fallback",
        queueDepth,
        queueMode,
        sessionKey: route.sessionKey,
        inflight: true,
      };
    },

    dispatchTaskInference: async (request: WTTTaskInferenceRuntimeRequest) => {
      let topicId = request.task.topicId?.trim();

      if (!topicId || topicId === "-") {
        const token = params.account?.token?.trim();
        const cloudUrl = params.account?.cloudUrl?.trim();

        if (token && cloudUrl) {
          try {
            const resp = await fetch(`${cloudUrl.replace(/\/$/, "")}/tasks/${encodeURIComponent(request.taskId)}`, {
              method: "GET",
              headers: {
                Accept: "application/json",
                Authorization: `Bearer ${token}`,
                "X-Agent-Token": token,
              },
            });

            if (resp.ok) {
              const detail = await resp.json() as Record<string, unknown>;
              const fromDetail = toOptionalString(detail.topic_id) ?? toOptionalString(detail.topicId);
              if (fromDetail && fromDetail !== "-") {
                topicId = fromDetail;
              }
            }
          } catch {
            // keep fallback below
          }
        }
      }

      if (!topicId || topicId === "-") {
        throw new Error(`task_topic_unresolved:${request.taskId}`);
      }

      const emitTypingSignal = async (state: "start" | "stop"): Promise<void> => {
        if (!params.typingSignal) return;
        try {
          await params.typingSignal({ topicId, state, ttlMs: 6000 });
        } catch {
          // best-effort only
        }
      };

      const route = runtime.routing.resolveAgentRoute({
        cfg: params.cfg,
        channel: CHANNEL_ID,
        accountId: params.accountId,
        peer: { kind: "group", id: topicId },
      });

      const storePath = runtime.session.resolveStorePath(params.cfg.session?.store, {
        agentId: route.agentId,
      });

      const previousTimestamp = runtime.session.readSessionUpdatedAt({
        storePath,
        sessionKey: route.sessionKey,
      });
      const runStartedMs = Date.now();

      const timestamp = new Date().toISOString();
      const from = `wtt:topic:${topicId}`;
      const to = `topic:${topicId}`;
      const chatType = "group";

      const envelopeOptions = runtime.reply.resolveEnvelopeFormatOptions(params.cfg);
      const body = runtime.reply.formatAgentEnvelope({
        channel: "WTT",
        from: "WTT Task Executor",
        timestamp,
        previousTimestamp,
        envelope: envelopeOptions,
        body: request.prompt,
      });

      const ctxPayload = runtime.reply.finalizeInboundContext({
        Body: body,
        BodyForAgent: request.prompt,
        RawBody: request.prompt,
        CommandBody: request.prompt,
        From: from,
        To: to,
        SessionKey: route.sessionKey,
        AccountId: route.accountId,
        ChatType: chatType,
        ConversationLabel: `topic:${topicId}`,
        SenderName: "WTT Task Executor",
        SenderId: params.account?.agentId || "wtt-task-executor",
        GroupSubject: topicId,
        Provider: CHANNEL_ID,
        Surface: CHANNEL_ID,
        MessageSid: `task-run:${request.taskId}:${Date.now()}`,
        Timestamp: timestamp,
        OriginatingChannel: CHANNEL_ID,
        OriginatingTo: to,
      });

      await runtime.session.recordInboundSession({
        storePath,
        sessionKey: route.sessionKey,
        ctx: ctxPayload,
        updateLastRoute: {
          sessionKey: route.sessionKey,
          channel: CHANNEL_ID,
          to,
          accountId: route.accountId,
        },
        onRecordError: () => {
          // keep inference path running even if session recording fails
        },
      });

      const chunks: string[] = [];
      let dispatchResult: unknown;

      await emitTypingSignal("start");
      try {
        dispatchResult = await runtime.reply.dispatchReplyWithBufferedBlockDispatcher({
          ctx: ctxPayload,
          cfg: params.cfg,
          dispatcherOptions: {
            deliver: async (payload) => {
              if (payload.isReasoning) return;
              const text = extractDispatchText(payload);
              if (text) chunks.push(text);
            },
          },
        });
      } finally {
        await emitTypingSignal("stop");
      }

      const fallback = extractDispatchText(dispatchResult);
      const outputText = chunks.join("\n\n").trim() || fallback;

      const usage = await collectSessionUsageDelta({
        storePath,
        sessionKey: route.sessionKey,
        sinceMs: runStartedMs,
        untilMs: Date.now(),
      });

      return {
        outputText,
        provider: "channelRuntime.reply.dispatchReplyWithBufferedBlockDispatcher",
        usage,
        raw: dispatchResult,
      };
    },
  };
}

export async function processWTTCommandText(params: {
  text: string;
  accountId?: string;
  cfg?: OpenClawConfig;
  channelRuntime?: ChannelRuntimeLike;
}): Promise<WTTCommandProcessResult> {
  const accountId = params.accountId ?? DEFAULT_ACCOUNT_ID;
  const account = resolveCommandAccountContext(accountId, params.cfg);

  return commandRouter.processText(params.text, {
    accountId,
    account,
    runtimeHooks: createTaskInferenceRuntimeHooks({
      cfg: params.cfg ?? {},
      accountId,
      account,
      channelRuntime: params.channelRuntime,
    }),
  });
}

type PluginAPI = {
  log: (level: "debug" | "info" | "warn" | "error", msg: string, data?: unknown) => void;
  onMessage?: (accountId: string, msg: WsNewMessage) => void;
  onTaskStatus?: (accountId: string, msg: WsTaskStatus) => void;
};

async function resolveAgentDisplayName(account: ResolvedWTTAccount): Promise<string | undefined> {
  const token = account.token?.trim();
  const agentId = account.agentId?.trim();
  if (!token || !agentId) return undefined;

  const authHeaders = {
    Accept: "application/json",
    Authorization: `Bearer ${token}`,
    "X-Agent-Token": token,
  };

  // Preferred endpoint: lists current user's bound agents including display_name.
  try {
    const myResp = await fetch(`${account.cloudUrl.replace(/\/$/, "")}/agents/my`, {
      method: "GET",
      headers: authHeaders,
    });
    if (myResp.ok) {
      const payload = await myResp.json() as unknown;
      const rows = Array.isArray(payload)
        ? payload
        : (payload && typeof payload === "object" && Array.isArray((payload as Record<string, unknown>).agents))
          ? (payload as Record<string, unknown>).agents as unknown[]
          : [];

      for (const rowRaw of rows) {
        if (!rowRaw || typeof rowRaw !== "object") continue;
        const row = rowRaw as Record<string, unknown>;
        const rowId = typeof row.agent_id === "string" ? row.agent_id.trim() : "";
        if (rowId !== agentId) continue;
        const display = typeof row.display_name === "string" ? row.display_name.trim() : "";
        if (display) return display;
      }
    }
  } catch {
    // ignore and try fallback endpoint
  }

  // Fallback endpoint.
  try {
    const profileResp = await fetch(`${account.cloudUrl.replace(/\/$/, "")}/agents/${encodeURIComponent(agentId)}/profile`, {
      method: "GET",
      headers: authHeaders,
    });
    if (profileResp.ok) {
      const profile = await profileResp.json() as { display_name?: string };
      const display = profile.display_name?.trim();
      if (display) return display;
    }
  } catch {
    // ignore
  }

  return undefined;
}

async function startWsAccount(
  accountId: string,
  account: ResolvedWTTAccount,
  api: PluginAPI,
): Promise<WTTCloudClient | undefined> {
  const existing = clients.get(accountId);
  if (existing) {
    existing.disconnect();
    clients.delete(accountId);
  }

  if (!account.enabled || !account.configured) {
    api.log("info", `WTT account ${accountId} skipped (${!account.enabled ? "disabled" : "not configured"})`);
    return undefined;
  }

  await ensureAccountE2EPassword(accountId, account, api.log);

  const client = new WTTCloudClient({
    account,
    onMessage: (msg) => api.onMessage?.(accountId, msg),
    onTaskStatus: (msg) => api.onTaskStatus?.(accountId, msg),
    onConnect: () => api.log("info", `[${accountId}] connected`),
    onDisconnect: () => api.log("info", `[${accountId}] disconnected`),
    onError: (err) => api.log("error", `[${accountId}] ${err.message}`),
    log: (level, msg, data) => api.log(level, `[${accountId}] ${msg}`, data),
  });

  clients.set(accountId, client);
  await client.connect();

  // Resolve display name from server (supports claimed+renamed agent names).
  try {
    const displayName = await resolveAgentDisplayName(account);
    if (displayName && displayName !== account.agentId) {
      account.name = displayName;
      api.log("info", `[${accountId}] display name resolved: ${displayName}`);
    }
  } catch {
    // Non-critical — inference gating will still match agentId.
  }

  return client;
}

async function stopAccount(accountId: string): Promise<void> {
  const client = clients.get(accountId);
  if (!client) return;
  client.disconnect();
  clients.delete(accountId);
}

function parseWttTarget(rawTarget: string):
  | { mode: "topic"; value: string }
  | { mode: "p2p"; value: string } {
  const target = (rawTarget || "").trim();

  if (target.startsWith("topic:")) return { mode: "topic", value: target.slice("topic:".length).trim() };
  if (target.startsWith("p2p:")) return { mode: "p2p", value: target.slice("p2p:".length).trim() };
  if (target.startsWith("agent:")) return { mode: "p2p", value: target.slice("agent:".length).trim() };

  // default behavior: treat as topic id for compatibility with existing topic-based routing
  return { mode: "topic", value: target };
}

async function sendText(params: {
  to: string;
  text: string;
  accountId?: string;
  cfg?: OpenClawConfig;
}): Promise<{ channel: "wtt"; messageId: string; conversationId?: string; meta?: Record<string, unknown> }> {
  const accountId = params.accountId ?? DEFAULT_ACCOUNT_ID;
  const client = getClient(accountId);
  if (!client?.connected) throw new Error(`WTT account ${accountId} is not connected`);

  const target = parseWttTarget(params.to);
  await runHooks("before", { tool: "sendText", args: { ...params, target } });

  let response: any;
  const account = client.getAccount();
  const p2pEncryptEnabled = isP2PE2EEnabled(account) && client.hasE2EKey();

  if (target.mode === "p2p") {
    response = await client.p2p(target.value, params.text, p2pEncryptEnabled);
  } else {
    const shouldEncryptTopic = p2pEncryptEnabled && isP2PTopicId(target.value);
    response = await client.publish(target.value, params.text, { encrypt: shouldEncryptTopic });
  }

  await runHooks("after", { tool: "sendText", args: { ...params, target }, result: response });

  return {
    channel: "wtt",
    messageId: String(response?.id ?? response?.message_id ?? response?.request_id ?? Date.now()),
    conversationId: String(response?.topic_id ?? target.value),
    meta: {
      mode: target.mode,
      raw: response ?? null,
    },
  };
}

async function sendMedia(params: {
  to: string;
  text?: string;
  mediaUrl?: string;
  accountId?: string;
  cfg?: OpenClawConfig;
}): Promise<{ channel: "wtt"; messageId: string; conversationId?: string; meta?: Record<string, unknown> }> {
  const payload = JSON.stringify({
    type: "media",
    mediaUrl: params.mediaUrl ?? "",
    caption: params.text ?? "",
  });
  return sendText({
    to: params.to,
    text: payload,
    accountId: params.accountId,
    cfg: params.cfg,
  });
}

function waitForAbort(signal: AbortSignal): Promise<void> {
  if (signal.aborted) return Promise.resolve();
  return new Promise((resolve) => {
    signal.addEventListener(
      "abort",
      () => {
        resolve();
      },
      { once: true },
    );
  });
}

function toIsoTimestamp(raw: unknown): string {
  if (typeof raw === "string" && raw.trim()) {
    const d = new Date(raw);
    if (!Number.isNaN(d.getTime())) return d.toISOString();
    return raw;
  }
  if (typeof raw === "number" && Number.isFinite(raw)) {
    const d = new Date(raw);
    if (!Number.isNaN(d.getTime())) return d.toISOString();
  }
  return new Date().toISOString();
}

function toOptionalString(value: unknown): string | undefined {
  if (typeof value !== "string") return undefined;
  const trimmed = value.trim();
  return trimmed ? trimmed : undefined;
}

function hasMeaningfulPipelineId(value: unknown): boolean {
  const normalized = String(value ?? "").trim().toLowerCase();
  if (!normalized) return false;
  if (["default", "none", "null", "undefined", "n/a", "na", "-", "0"].includes(normalized)) {
    return false;
  }
  return true;
}

function sanitizeInboundText(raw: string): string {
  let text = raw || "";

  // Strip WTT source marker banner block if present.
  text = text.replace(/┌─ 来源标识[\s\S]*?└[^\n]*\n?/g, "").trim();

  return text;
}

function isMeaningfulUserText(text: string): boolean {
  const t = (text || "").trim();
  if (!t) return false;

  // Drop visual-only box characters/separators.
  const visualOnly = t.replace(/[\s│┌┐└┘─\-_=]+/g, "").trim();
  if (!visualOnly) return false;

  // Drop status heartbeat style lines from execution stream.
  if (/^\[\d{4}-\d{2}-\d{2}T[^\]]+\]\s*状态=/.test(t)) return false;
  if (/^状态=.+\|\s*动作=.+\|\s*心跳=\d+s$/i.test(t)) return false;

  return true;
}

function isSystemLikeInbound(raw: WsMessagePayload & Record<string, unknown>, text: string): boolean {
  const semanticType = String(raw.semantic_type ?? "").toLowerCase();
  const senderType = String(raw.sender_type ?? "").toLowerCase();
  const contentType = String(raw.content_type ?? "").toLowerCase();

  if (senderType === "system") return true;
  if (semanticType.startsWith("system") || semanticType === "task_progress") return true;
  if (["task_request", "task_run", "task_status", "task_summary", "task_blocked", "task_review", "notification"].includes(semanticType)) {
    return true;
  }
  if (contentType === "system") return true;
  if (text.startsWith("[system:")) return true;

  return false;
}

function isTaskBootstrapPlaceholderText(text: string): boolean {
  const t = (text || "").trim().toLowerCase();
  if (!t) return true;
  return t === "new task" || t === "新任务" || t === "(无描述)" || t === "无描述";
}

function isBlockedDiscussModelCommand(raw: WsMessagePayload & Record<string, unknown>, text: string): boolean {
  const topicType = String(raw.topic_type ?? "").toLowerCase();
  if (topicType !== "discussion") return false;

  // Task-linked discussion topics must keep model selection available.
  const taskId = toOptionalString(raw.task_id);
  const topicName = String(raw.topic_name ?? "");
  const isTaskLinked = Boolean(taskId || topicName.startsWith("TASK-"));
  if (isTaskLinked) return false;

  const normalized = (text || "").trim().toLowerCase();
  return /^\/models?(\s|$)/.test(normalized);
}

function normalizeMentionToken(raw: string): string {
  const lowered = (raw || "")
    .normalize("NFKC")
    .trim()
    .replace(/^@+/, "")
    .toLowerCase();

  return lowered.replace(/[^\p{L}\p{N}]+/gu, "");
}

function extractMentionHandles(content: string): string[] {
  const handles = new Set<string>();

  // Parse @mentions as agent-like handles using ASCII-safe token rules.
  // Why:
  // - Discuss topics often contain CJK text immediately after mention, e.g. "@lyz_agent看看"
  // - Unicode-wide token regex may swallow trailing CJK and produce "lyzagent看看"
  // - We need strict/precise handle extraction for routing gate.
  const regex = /(^|[^A-Za-z0-9_])@([A-Za-z0-9][A-Za-z0-9._-]{0,63})/g;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(content)) !== null) {
    const token = normalizeMentionToken(match[2] || "");
    if (token) handles.add(token);
  }

  return Array.from(handles);
}

function buildAgentMentionAliases(agentId: string, agentName?: string): Set<string> {
  const aliases = new Set<string>();

  const addAlias = (candidate?: string): void => {
    if (!candidate) return;
    const normalized = normalizeMentionToken(candidate);
    if (normalized) aliases.add(normalized);
  };

  addAlias(agentId);

  if (agentName) {
    addAlias(agentName);
    addAlias(agentName.replace(/\s+/g, "_"));
    addAlias(agentName.replace(/\s+/g, "-"));
  }

  return aliases;
}

function resolveMentionMatch(content: string, agentId: string, agentName?: string): {
  hasMentions: boolean;
  matchesAgent: boolean;
} {
  const mentions = extractMentionHandles(content || "");
  if (mentions.length === 0) {
    return { hasMentions: false, matchesAgent: false };
  }

  const aliases = buildAgentMentionAliases(agentId, agentName);
  const matchesAgent = mentions.some((mention) => aliases.has(mention));

  return {
    hasMentions: true,
    matchesAgent,
  };
}

function matchesAgentIdentity(candidate: string | undefined, agentId: string, agentName?: string): boolean {
  const normalized = normalizeMentionToken(candidate ?? "");
  if (!normalized) return false;

  const aliases = buildAgentMentionAliases(agentId, agentName);
  return aliases.has(normalized);
}

function isStandaloneSlashCommandText(text: string): boolean {
  const trimmed = text.trim();
  if (!trimmed.startsWith("/")) return false;
  if (trimmed.includes("\n")) return false;
  return /^\/[a-z][a-z0-9_:-]*(?:\s+[\s\S]*)?$/i.test(trimmed);
}

function normalizeSlashForWttCommandRouter(text: string, account: ResolvedWTTAccount): string {
  const trimmed = text.trim();
  if (!trimmed.startsWith("/")) return text;

  const prefixOnly = account.config.slashCompatWttPrefixOnly ?? DEFAULT_SLASH_COMPAT_WTT_PREFIX_ONLY;
  if (prefixOnly) return text;

  const aliasMap: Record<string, string> = {
    task: "task",
    pipeline: "pipeline",
    pipe: "pipeline",
    delegate: "delegate",
    list: "list",
    find: "find",
    join: "join",
    leave: "leave",
    publish: "publish",
    poll: "poll",
    history: "history",
    p2p: "p2p",
    detail: "detail",
    subscribed: "subscribed",
    config: "config",
    cfg: "config",
    bind: "bind",
    whoami: "whoami",
    help: "help",
  };

  const match = trimmed.match(/^\/([a-z][a-z0-9_:-]*)(?:\s+([\s\S]*))?$/i);
  if (!match) return text;

  const verb = match[1].toLowerCase();
  if (verb === "wtt") return text;
  const mapped = aliasMap[verb];
  if (!mapped) return text;

  const args = (match[2] ?? "").trim();
  return args ? `/wtt ${mapped} ${args}` : `/wtt ${mapped}`;
}

/**
 * Inference gating: decide if this inbound message should trigger LLM reasoning.
 *
 * Rules:
 * - Broadcast topics never trigger.
 * - Task-linked topics do not require @mention; runner_agent_id/name is used when available.
 * - Discussion topics require explicit @mention for this agent.
 * - P2P topics never require @mention.
 */
function shouldTriggerInference(
  raw: WsMessagePayload & Record<string, unknown>,
  agentId: string,
  agentName?: string,
): { trigger: boolean; reason?: string } {
  const topicType = String(raw.topic_type ?? "").toLowerCase();

  // Broadcast topics — never auto-infer.
  if (topicType === "broadcast") {
    return { trigger: false, reason: "broadcast_no_infer" };
  }

  const taskId = toOptionalString(raw.task_id);
  const topicName = String(raw.topic_name ?? "");
  const isTaskLinked = Boolean(taskId || topicName.startsWith("TASK-"));

  if (isTaskLinked) {
    const senderType = String(raw.sender_type ?? "").toLowerCase();
    if (senderType && senderType !== "human" && senderType !== "user") {
      return { trigger: false, reason: "task_non_human_sender" };
    }
    const runnerAgentId = toOptionalString(raw.runner_agent_id) ?? toOptionalString(raw.runnerAgentId);
    const runnerAgentName = toOptionalString(raw.runner_agent_name) ?? toOptionalString(raw.runnerAgentName);
    if (runnerAgentId || runnerAgentName) {
      if (
        matchesAgentIdentity(runnerAgentId, agentId, agentName)
        || matchesAgentIdentity(runnerAgentName, agentId, agentName)
      ) {
        return { trigger: true, reason: "task_linked_runner_match" };
      }
      return { trigger: false, reason: "task_runner_mismatch" };
    }

    return { trigger: true, reason: "task_linked" };
  }

  // Only discuss topics require explicit mention.
  // Fallback: accept backend-resolved runner targeting for renamed agent names.
  if (topicType === "discussion") {
    const content = String(raw.content ?? "");
    const mentionMatch = resolveMentionMatch(content, agentId, agentName);
    if (mentionMatch.matchesAgent) {
      return { trigger: true };
    }

    const runnerAgentId = toOptionalString(raw.runner_agent_id) ?? toOptionalString(raw.runnerAgentId);
    const runnerAgentName = toOptionalString(raw.runner_agent_name) ?? toOptionalString(raw.runnerAgentName);
    if (
      matchesAgentIdentity(runnerAgentId, agentId, agentName)
      || matchesAgentIdentity(runnerAgentName, agentId, agentName)
    ) {
      return { trigger: true, reason: "discussion_runner_match" };
    }

    return { trigger: false, reason: "discussion_no_mention" };
  }

  // p2p / collaborative / unknown — infer by default.
  return { trigger: true };
}

function toPositiveInt(raw: unknown, fallback: number): number {
  const n = Number(raw);
  if (!Number.isFinite(n) || n <= 0) return fallback;
  return Math.floor(n);
}

function asRecord(value: unknown): Record<string, unknown> | undefined {
  if (!value || typeof value !== "object") return undefined;
  return value as Record<string, unknown>;
}

function parseInboundMetadata(raw: WsMessagePayload & Record<string, unknown>): Record<string, unknown> | undefined {
  const direct = raw.metadata;
  if (direct && typeof direct === "object") return direct as Record<string, unknown>;
  if (typeof direct === "string") {
    try {
      const parsed = JSON.parse(direct) as unknown;
      return parsed && typeof parsed === "object" ? parsed as Record<string, unknown> : undefined;
    } catch {
      return undefined;
    }
  }
  return undefined;
}

function coerceWsNewMessage(raw: unknown): WsNewMessage | undefined {
  const record = asRecord(raw);
  if (!record) return undefined;

  const wrapped = asRecord(record.message);
  if (record.type === "new_message" && wrapped) {
    return {
      type: "new_message",
      message: wrapped as unknown as WsMessagePayload,
    };
  }

  if (wrapped && toOptionalString(wrapped.id)) {
    return {
      type: "new_message",
      message: wrapped as unknown as WsMessagePayload,
    };
  }

  if (toOptionalString(record.id) && resolveInboundTopicId(record as unknown as WsMessagePayload & Record<string, unknown>) && toOptionalString(record.sender_id)) {
    return {
      type: "new_message",
      message: record as unknown as WsMessagePayload,
    };
  }

  return undefined;
}

export function extractPolledInboundMessages(raw: unknown): WsNewMessage[] {
  let candidates: unknown[] = [];

  if (Array.isArray(raw)) {
    candidates = raw;
  } else {
    const record = asRecord(raw);
    const nested = asRecord(record?.data);
    if (Array.isArray(record?.messages)) candidates = record!.messages as unknown[];
    else if (Array.isArray(record?.data)) candidates = record!.data as unknown[];
    else if (Array.isArray(nested?.messages)) candidates = nested!.messages as unknown[];
    else if (Array.isArray(nested?.items)) candidates = nested!.items as unknown[];
  }

  const parsed: WsNewMessage[] = [];
  for (const item of candidates) {
    const msg = coerceWsNewMessage(item);
    if (msg) parsed.push(msg);
  }

  return parsed;
}

function resolveInboundTopicId(msg: WsMessagePayload & Record<string, unknown>): string {
  const direct = toOptionalString(msg.topic_id) ?? toOptionalString(msg.topicId) ?? toOptionalString(msg.p2p_topic_id);
  if (direct) return direct;

  const nestedTopic = asRecord(msg.topic);
  const nestedId = nestedTopic ? toOptionalString(nestedTopic.id) : undefined;
  if (nestedId) return nestedId;

  return "";
}

function resolveInboundDedupKey(msg: WsNewMessage): string {
  const payload = msg.message as WsMessagePayload & Record<string, unknown>;
  const directId = toOptionalString(payload.id);
  if (directId) return directId;

  const topicId = resolveInboundTopicId(payload) || "no-topic";
  const senderId = toOptionalString(payload.sender_id) ?? "unknown";
  const createdAt = toOptionalString(payload.created_at) ?? "";
  const content = String(payload.content ?? "").slice(0, 96);
  return `${topicId}:${senderId}:${createdAt}:${content}`;
}

function isLikelyP2PMessage(msg: WsMessagePayload & Record<string, unknown>): boolean {
  const topicType = String(msg.topic_type ?? "").toLowerCase();
  if (topicType === "p2p") return true;

  const topicId = resolveInboundTopicId(msg);

  // Legacy p2p push payloads only contain id/topic_id/sender_id/content/created_at/encrypted.
  // If type hints are absent and we still have a topic+sender, treat as p2p.
  if (!topicType && topicId && msg.sender_id && !msg.content_type && !msg.semantic_type && !msg.sender_type) {
    return true;
  }

  // Current deployment only enables encryption on P2P; if we observe encrypted payload
  // without explicit topic_type (e.g. poll fallback), treat as P2P for routing/encryption cache.
  if (!topicType && topicId && Boolean(msg.encrypted)) {
    return true;
  }

  return false;
}

export type NormalizedInboundWsMessage = {
  text: string;
  senderId: string;
  senderName?: string;
  topicId: string;
  topicName?: string;
  messageId: string;
  timestamp: string;
  chatType: "direct" | "group";
  routePeerId: string;
  to: string;
  from: string;
  conversationLabel: string;
  /** Image URLs extracted from message content (HTML <img> or markdown ![](url)) */
  mediaUrls: string[];
  mediaTypes: string[];
};

export function normalizeInboundWsMessage(params: {
  msg: WsNewMessage;
  decryptedContent?: string;
}): NormalizedInboundWsMessage {
  const raw = params.msg.message as WsMessagePayload & Record<string, unknown>;
  const senderId = String(raw.sender_id || "unknown");
  const topicId = resolveInboundTopicId(raw);
  const senderName = toOptionalString(raw.sender_display_name);
  const topicName = toOptionalString(raw.topic_name);

  const content = sanitizeInboundText(params.decryptedContent ?? String(raw.content ?? ""));
  const messageId = toOptionalString(raw.id) ?? `${topicId || "no-topic"}:${senderId}:${Date.now()}`;
  const timestamp = toIsoTimestamp(raw.created_at);

  // Extract image URLs from content for OpenClaw media-understanding pipeline
  const mediaUrls: string[] = [];
  const mediaTypes: string[] = [];
  // HTML <img src="url"> pattern (from Tiptap rich editor)
  const htmlImgRe = /<img\s[^>]*\bsrc\s*=\s*"(https?:\/\/[^"]+)"/gi;
  let htmlMatch: RegExpExecArray | null;
  while ((htmlMatch = htmlImgRe.exec(content)) !== null) {
    mediaUrls.push(htmlMatch[1]);
    mediaTypes.push("image/png");
  }
  // Markdown ![alt](url) pattern (from chat input)
  const mdImgRe = /!\[[^\]]*\]\((https?:\/\/[^\s)]+)\)/gi;
  let mdMatch: RegExpExecArray | null;
  while ((mdMatch = mdImgRe.exec(content)) !== null) {
    if (!mediaUrls.includes(mdMatch[1])) {
      mediaUrls.push(mdMatch[1]);
      mediaTypes.push("image/png");
    }
  }
  // Bare image URLs on their own line
  const bareImgRe = /^(https?:\/\/\S+\.(?:jpg|jpeg|png|gif|webp|svg)(?:\?[^\s]*)?)$/gim;
  let bareMatch: RegExpExecArray | null;
  while ((bareMatch = bareImgRe.exec(content)) !== null) {
    if (!mediaUrls.includes(bareMatch[1])) {
      mediaUrls.push(bareMatch[1]);
      mediaTypes.push("image/png");
    }
  }

  const isP2P = isLikelyP2PMessage(raw);
  const hasTopicId = Boolean(topicId);
  const chatType: "direct" | "group" = isP2P ? "direct" : "group";
  const routePeerId = isP2P
    ? (hasTopicId ? topicId : senderId)
    : topicId || senderId;
  // Always publish to the specific topic_id so responses land in the correct
  // P2P topic (e.g. worker topics vs default P2P between the same two parties).
  const to = hasTopicId ? `topic:${topicId}` : `p2p:${senderId}`;
  const from = `wtt:${senderId}`;

  const conversationLabel = isP2P
    ? `p2p:${topicName ?? senderName ?? (hasTopicId ? topicId : senderId)}`
    : `topic:${topicName ?? (topicId || "unknown")}`;

  return {
    text: content,
    senderId,
    senderName,
    topicId,
    topicName,
    messageId,
    timestamp,
    chatType,
    routePeerId,
    to,
    from,
    conversationLabel,
    mediaUrls,
    mediaTypes,
  };
}

export type InboundRoutingResult = {
  routed: boolean;
  reason?: "runtime_unavailable" | "self_echo" | "empty_message" | "system_message" | "agent_no_mention" | "broadcast_no_infer" | "discussion_no_mention" | "task_runner_mismatch" | "task_non_human_sender";
};

export type InboundRelayStats = {
  pushReceivedCount: number;
  pollFetchedCount: number;
  routedCount: number;
  dedupDroppedCount: number;
};

export function createInboundMessageRelay(params: {
  cfg: OpenClawConfig;
  accountId: string;
  account: ResolvedWTTAccount;
  getLatestAccount?: () => ResolvedWTTAccount;
  channelRuntime?: ChannelRuntimeLike;
  decryptContent?: (content: string) => Promise<string>;
  deliver?: (params: { to: string; payload: Record<string, unknown> }) => Promise<void>;
  typingSignal?: (params: { topicId: string; state: "start" | "stop"; ttlMs?: number }) => Promise<void>;
  log?: (level: "debug" | "info" | "warn" | "error", msg: string, data?: unknown) => void;
  dedupWindowMs?: number;
  dedupMaxEntries?: number;
}): {
  stats: InboundRelayStats;
  handlePush: (msg: WsNewMessage) => Promise<InboundRoutingResult>;
  handlePollResult: (rawPollResult: unknown) => Promise<{ fetched: number; routed: number; dedupDropped: number }>;
} {
  const dedupWindowMs = toPositiveInt(params.dedupWindowMs, DEFAULT_INBOUND_DEDUP_WINDOW_MS);
  const dedupMaxEntries = toPositiveInt(params.dedupMaxEntries, DEFAULT_INBOUND_DEDUP_MAX_ENTRIES);
  const dedupSeenAt = new Map<string, number>();

  const stats: InboundRelayStats = {
    pushReceivedCount: 0,
    pollFetchedCount: 0,
    routedCount: 0,
    dedupDroppedCount: 0,
  };

  const pruneDedup = (nowMs: number): void => {
    const ttlCutoff = nowMs - dedupWindowMs;
    for (const [id, seenAt] of dedupSeenAt) {
      if (seenAt >= ttlCutoff) break;
      dedupSeenAt.delete(id);
    }

    while (dedupSeenAt.size > dedupMaxEntries) {
      const oldest = dedupSeenAt.keys().next().value;
      if (!oldest) break;
      dedupSeenAt.delete(oldest);
    }
  };

  const isDuplicate = (msg: WsNewMessage): boolean => {
    const key = resolveInboundDedupKey(msg);
    const nowMs = Date.now();
    pruneDedup(nowMs);
    const seenAt = dedupSeenAt.get(key);
    if (typeof seenAt === "number" && nowMs - seenAt <= dedupWindowMs) {
      return true;
    }

    dedupSeenAt.set(key, nowMs);
    return false;
  };

  const routeOne = async (msg: WsNewMessage, source: "push" | "poll"): Promise<InboundRoutingResult> => {
    if (isDuplicate(msg)) {
      stats.dedupDroppedCount += 1;
      params.log?.(
        "debug",
        `[${params.accountId}] inbound dedup dropped source=${source} dedup_dropped=${stats.dedupDroppedCount}`,
      );
      return { routed: false };
    }

    const result = await routeInboundWsMessage({
      cfg: params.cfg,
      accountId: params.accountId,
      account: params.getLatestAccount?.() ?? params.account,
      msg,
      channelRuntime: params.channelRuntime,
      decryptContent: params.decryptContent,
      deliver: params.deliver,
      typingSignal: params.typingSignal,
      log: params.log,
    });

    if (result.routed) stats.routedCount += 1;

    params.log?.(
      "debug",
      `[${params.accountId}] inbound counters push_received=${stats.pushReceivedCount} poll_fetched=${stats.pollFetchedCount} routed=${stats.routedCount} dedup_dropped=${stats.dedupDroppedCount}`,
    );

    return result;
  };

  return {
    stats,
    async handlePush(msg: WsNewMessage): Promise<InboundRoutingResult> {
      stats.pushReceivedCount += 1;
      return routeOne(msg, "push");
    },
    async handlePollResult(rawPollResult: unknown): Promise<{ fetched: number; routed: number; dedupDropped: number }> {
      const messages = extractPolledInboundMessages(rawPollResult);
      stats.pollFetchedCount += messages.length;

      const beforeRouted = stats.routedCount;
      const beforeDedup = stats.dedupDroppedCount;

      for (const msg of messages) {
        await routeOne(msg, "poll");
      }

      const routed = stats.routedCount - beforeRouted;
      const dedupDropped = stats.dedupDroppedCount - beforeDedup;
      params.log?.(
        "info",
        `[${params.accountId}] inbound poll fetched=${messages.length} routed=${routed} dedup_dropped=${dedupDropped} totals(push=${stats.pushReceivedCount},poll=${stats.pollFetchedCount},routed=${stats.routedCount},dedup=${stats.dedupDroppedCount})`,
      );

      return {
        fetched: messages.length,
        routed,
        dedupDropped,
      };
    },
  };
}

async function deliverReplyPayload(params: {
  to: string;
  payload: Record<string, unknown>;
  accountId: string;
  cfg: OpenClawConfig;
}): Promise<void> {
  const text = typeof params.payload.text === "string" ? params.payload.text : "";
  const isReasoning = Boolean(params.payload.isReasoning);
  if (isReasoning) return;

  const mediaUrls = Array.isArray(params.payload.mediaUrls)
    ? params.payload.mediaUrls.filter((item): item is string => typeof item === "string" && item.trim().length > 0)
    : [];

  const mediaUrl = typeof params.payload.mediaUrl === "string" ? params.payload.mediaUrl.trim() : "";
  if (mediaUrl) mediaUrls.push(mediaUrl);

  if (mediaUrls.length > 0) {
    let first = true;
    for (const media of mediaUrls) {
      await sendMedia({
        to: params.to,
        text: first ? text : "",
        mediaUrl: media,
        accountId: params.accountId,
        cfg: params.cfg,
      });
      first = false;
    }
    return;
  }

  if (!text) return;

  await sendText({
    to: params.to,
    text,
    accountId: params.accountId,
    cfg: params.cfg,
  });
}

export async function routeInboundWsMessage(params: {
  cfg: OpenClawConfig;
  accountId: string;
  account: ResolvedWTTAccount;
  msg: WsNewMessage;
  channelRuntime?: ChannelRuntimeLike;
  decryptContent?: (content: string) => Promise<string>;
  deliver?: (params: { to: string; payload: Record<string, unknown> }) => Promise<void>;
  typingSignal?: (params: { topicId: string; state: "start" | "stop"; ttlMs?: number }) => Promise<void>;
  log?: (level: "debug" | "info" | "warn" | "error", msg: string, data?: unknown) => void;
}): Promise<InboundRoutingResult> {
  const runtime = params.channelRuntime;
  if (!runtime) {
    params.log?.("warn", `[${params.accountId}] channelRuntime unavailable; inbound message skipped`);
    return { routed: false, reason: "runtime_unavailable" };
  }

  const rawContent = String(params.msg.message.content ?? "");
  let decryptedContent = rawContent;
  if (params.msg.message.encrypted && params.decryptContent) {
    try {
      decryptedContent = await params.decryptContent(rawContent);
    } catch (err) {
      params.log?.("warn", `[${params.accountId}] Failed to decrypt inbound content, using raw`, err);
      decryptedContent = rawContent;
    }
  }

  const normalized = normalizeInboundWsMessage({
    msg: params.msg,
    decryptedContent,
  });

  const rawMsg = params.msg.message as WsMessagePayload & Record<string, unknown>;
  const inboundTaskId = toOptionalString(rawMsg.task_id);
  const inferredTopicType = String(rawMsg.topic_type ?? "").toLowerCase();
  if (normalized.topicId) {
    if (inferredTopicType) {
      rememberTopicType(normalized.topicId, inferredTopicType);
    } else if (isLikelyP2PMessage(rawMsg)) {
      rememberTopicType(normalized.topicId, "p2p");
    }
  }
  const typingTopicId = normalized.topicId?.trim() || "";

  const emitTypingSignal = async (state: "start" | "stop"): Promise<void> => {
    if (!typingTopicId || !params.typingSignal) return;
    try {
      await params.typingSignal({ topicId: typingTopicId, state, ttlMs: 6000 });
    } catch (err) {
      params.log?.("debug", `[${params.accountId}] typing signal ${state} failed topic=${typingTopicId}`, err);
    }
  };

  const patchTaskStatus = async (taskId: string, status: string, notes?: string): Promise<boolean> => {
    if (!params.account.token) return false;

    try {
      const body: Record<string, unknown> = {
        status,
        runner_agent_id: params.account.agentId || undefined,
      };
      if (notes && notes.trim()) {
        body.notes = notes.trim();
      }

      const resp = await fetch(`${params.account.cloudUrl.replace(/\/$/, "")}/tasks/${encodeURIComponent(taskId)}`, {
        method: "PATCH",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          Authorization: `Bearer ${params.account.token}`,
          "X-Agent-Token": params.account.token,
        },
        body: JSON.stringify(body),
      });
      return resp.ok;
    } catch {
      return false;
    }
  };

  if (!isMeaningfulUserText(normalized.text)) {
    // Ignore empty/visual-only/status payloads to avoid creating empty task requests.
    return { routed: false, reason: "empty_message" };
  }

  if (isSystemLikeInbound(rawMsg, normalized.text)) {
    // Ignore transport/system chatter in user-facing conversation flow.
    return { routed: false, reason: "system_message" };
  }

  if (normalized.senderId === params.account.agentId) {
    // Ignore own echo to avoid self-reply loops.
    return { routed: false, reason: "self_echo" };
  }

  if (inboundTaskId && isTaskBootstrapPlaceholderText(normalized.text)) {
    // Ignore placeholder bootstrap text in task topics (e.g. default "New Task").
    return { routed: false, reason: "empty_message" };
  }

  if (isBlockedDiscussModelCommand(rawMsg, normalized.text)) {
    // In discussion topics, block model switching commands to avoid all agents
    // responding to the same slash command.
    return { routed: false, reason: "system_message" };
  }

  const slashCompatEnabled = params.account.config.slashCompat ?? DEFAULT_SLASH_COMPAT_ENABLED;
  const slashBypassMentionGate = params.account.config.slashBypassMentionGate ?? DEFAULT_SLASH_BYPASS_MENTION_GATE;

  const topicType = String(rawMsg.topic_type ?? "").toLowerCase();
  const topicName = String(rawMsg.topic_name ?? "");
  const isTaskLinkedTopic = Boolean(inboundTaskId || topicName.startsWith("TASK-"));
  const isSlashLike = /^\/\S+/.test((normalized.text || "").trim());
  const inboundMetadata = parseInboundMetadata(rawMsg);
  const mentionTargetedDiscussion = topicType === "discussion"
    && resolveMentionMatch(String(rawMsg.content ?? ""), params.account.agentId, params.account.name).matchesAgent;

  if (slashCompatEnabled) {
    if (topicType === "discussion" && !isTaskLinkedTopic && isSlashLike) {
      const targetAgentId = toOptionalString(inboundMetadata?.command_target_agent_id)
        ?? toOptionalString(inboundMetadata?.commandTargetAgentId);

      // For non-task discuss slash commands: execute only on explicitly targeted agent.
      if (!targetAgentId || !matchesAgentIdentity(targetAgentId, params.account.agentId, params.account.name)) {
        return { routed: false, reason: "agent_no_mention" };
      }
    }

    const wttCommandText = normalizeSlashForWttCommandRouter(normalized.text, params.account);
    const commandResult = await processWTTCommandText({
      text: wttCommandText,
      accountId: params.accountId,
      cfg: params.cfg,
      channelRuntime: runtime,
    });

    if (commandResult.handled) {
      const responseText = (commandResult.response ?? "").trim();
      if (responseText) {
        const payload = { text: responseText };
        if (params.deliver) {
          await params.deliver({
            to: normalized.to,
            payload,
          });
        } else {
          await deliverReplyPayload({
            to: normalized.to,
            payload,
            accountId: params.accountId,
            cfg: params.cfg,
          });
        }
      }

      params.log?.("info", `[${params.accountId}] command_router handled command=${commandResult.command ?? "unknown"}`);
      return { routed: true };
    }
  }

  const standaloneSlash = isStandaloneSlashCommandText(normalized.text);
  const bypassInferenceGate = slashCompatEnabled && slashBypassMentionGate && standaloneSlash;
  let inferDecision: { trigger: boolean; reason?: string } | undefined;

  // Inference gating: skip messages that shouldn't trigger reasoning
  if (!bypassInferenceGate) {
    inferDecision = shouldTriggerInference(rawMsg, params.account.agentId, params.account.name);
    params.log?.("info", `[${params.accountId}] inference_gate topic_type=${String(rawMsg.topic_type)} task_id=${String(rawMsg.task_id ?? "")} trigger=${inferDecision.trigger} reason=${inferDecision.reason ?? "ok"} content_preview=${String(rawMsg.content ?? "").slice(0, 60)} agentName=${params.account.name}`);
    if (!inferDecision.trigger) {
      return { routed: false, reason: inferDecision.reason as InboundRoutingResult["reason"] };
    }
  } else {
    params.log?.("info", `[${params.accountId}] inference_gate bypassed reason=slash_command topic_type=${String(rawMsg.topic_type)}`);
  }

  const route = runtime.routing.resolveAgentRoute({
    cfg: params.cfg,
    channel: CHANNEL_ID,
    accountId: params.accountId,
    peer: {
      kind: normalized.chatType,
      id: normalized.routePeerId,
    },
  });

  const storePath = runtime.session.resolveStorePath(params.cfg.session?.store, {
    agentId: route.agentId,
  });

  const previousTimestamp = runtime.session.readSessionUpdatedAt({
    storePath,
    sessionKey: route.sessionKey,
  });

  const envelopeOptions = runtime.reply.resolveEnvelopeFormatOptions(params.cfg);
  const fromLabel = normalized.chatType === "direct"
    ? normalized.senderName ?? normalized.senderId
    : `${normalized.senderName ?? normalized.senderId} @ ${normalized.topicName ?? (normalized.topicId || "topic")}`;

  const body = runtime.reply.formatAgentEnvelope({
    channel: "WTT",
    from: fromLabel,
    timestamp: normalized.timestamp,
    previousTimestamp,
    envelope: envelopeOptions,
    body: normalized.text,
  });

  const taskTitleCandidate =
    toOptionalString(rawMsg.task_title)
    ?? toOptionalString(rawMsg.taskTitle)
    ?? toOptionalString(rawMsg.title)
    ?? (normalized.topicName && !normalized.topicName.startsWith("TASK-") ? normalized.topicName : undefined);

  const mentionDirective = (topicType === "discussion" && mentionTargetedDiscussion)
    ? "注意：这是讨论话题中明确 @ 你的消息，必须直接回应用户问题，禁止输出 NO_REPLY。\n\n"
    : "";

  const bodyForAgent = inboundTaskId && taskTitleCandidate
    ? `${mentionDirective}任务标题: ${taskTitleCandidate}\n\n用户消息: ${normalized.text}`
    : `${mentionDirective}${normalized.text}`;

  const ctxPayload = runtime.reply.finalizeInboundContext({
    // Keep Body plain so downstream task/title extraction uses user text directly.
    Body: normalized.text,
    BodyForAgent: bodyForAgent,
    RawBody: normalized.text,
    CommandBody: normalized.text,
    EnvelopeBody: body,
    From: normalized.from,
    To: normalized.to,
    SessionKey: route.sessionKey,
    AccountId: route.accountId,
    ChatType: normalized.chatType,
    ConversationLabel: normalized.conversationLabel,
    SenderName: normalized.senderName,
    SenderId: normalized.senderId,
    GroupSubject: normalized.chatType === "group" ? normalized.topicName ?? normalized.topicId : undefined,
    Provider: CHANNEL_ID,
    Surface: CHANNEL_ID,
    MessageSid: normalized.messageId,
    Timestamp: normalized.timestamp,
    OriginatingChannel: CHANNEL_ID,
    OriginatingTo: normalized.to,
    // Pass extracted image URLs to OpenClaw media-understanding pipeline
    ...(normalized.mediaUrls.length > 0
      ? {
          MediaUrl: normalized.mediaUrls[0],
          MediaUrls: normalized.mediaUrls,
          MediaType: normalized.mediaTypes[0],
          MediaTypes: normalized.mediaTypes,
        }
      : {}),
  });

  const taskExecutorScope = (params.account.config.taskExecutorScope ?? "all").toLowerCase();
  let naturalBridgeTaskStatus = "";
  let naturalBridgeEnabled = false;
  let naturalBridgeDoingAtMs: number | null = null;

  // Natural bridge should work for normal (non-pipeline) tasks regardless of executor scope.
  if (inboundTaskId && params.account.token) {
    try {
      const detailResp = await fetch(`${params.account.cloudUrl.replace(/\/$/, "")}/tasks/${encodeURIComponent(inboundTaskId)}`, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${params.account.token}`,
          "X-Agent-Token": params.account.token,
        },
      });

      if (detailResp.ok) {
        const detailPayload = await detailResp.json() as Record<string, unknown>;
        const liveTaskType = String(detailPayload.task_type ?? detailPayload.taskType ?? "").trim().toLowerCase();
        const liveStatus = String(detailPayload.status ?? "").trim().toLowerCase();

        if (liveTaskType && liveTaskType !== "pipeline") {
          naturalBridgeEnabled = true;
          naturalBridgeTaskStatus = ["todo", "doing", "review", "done", "blocked"].includes(liveStatus)
            ? (liveStatus as typeof naturalBridgeTaskStatus)
            : "";

          // Delay todo->doing transition until we confirm meaningful output was delivered.
        }
      }
    } catch (err) {
      params.log?.("warn", `[${params.accountId}] natural task status bridge pre-dispatch failed task=${inboundTaskId}`, err);
    }
  }

  if (naturalBridgeEnabled && inboundTaskId && naturalBridgeTaskStatus === "todo" && isMeaningfulUserText(normalized.text)) {
    const movedDoing = await patchTaskStatus(inboundTaskId, "doing");
    if (movedDoing) {
      naturalBridgeTaskStatus = "doing";
      naturalBridgeDoingAtMs = Date.now();
    }
  }

  await runtime.session.recordInboundSession({
    storePath,
    sessionKey: route.sessionKey,
    ctx: ctxPayload,
    updateLastRoute: {
      sessionKey: route.sessionKey,
      channel: CHANNEL_ID,
      to: normalized.to,
      accountId: route.accountId,
    },
    onRecordError: (err) => {
      params.log?.("warn", `[${params.accountId}] Failed to record inbound session`, err);
    },
  });

  let dispatchProducedOutput = false;

  await emitTypingSignal("start");
  try {
    await runtime.reply.dispatchReplyWithBufferedBlockDispatcher({
      ctx: ctxPayload,
      cfg: params.cfg,
      dispatcherOptions: {
        deliver: async (payload) => {
          const isReasoning = Boolean(payload?.isReasoning);
          const text = typeof payload?.text === "string" ? payload.text.trim() : "";
          const mediaUrl = typeof payload?.mediaUrl === "string" ? payload.mediaUrl.trim() : "";
          const mediaUrls = Array.isArray(payload?.mediaUrls)
            ? payload.mediaUrls.filter((item): item is string => typeof item === "string" && item.trim().length > 0)
            : [];

          if (!isReasoning && (text.length > 0 || mediaUrl.length > 0 || mediaUrls.length > 0)) {
            dispatchProducedOutput = true;
          }

          if (params.deliver) {
            await params.deliver({
              to: normalized.to,
              payload,
            });
            return;
          }

          await deliverReplyPayload({
            to: normalized.to,
            payload,
            accountId: params.accountId,
            cfg: params.cfg,
          });
        },
        onError: (err, info) => {
          params.log?.(
            "error",
            `[${params.accountId}] WTT inbound dispatch failed (${String(info?.kind ?? "unknown")})`,
            err,
          );
        },
      },
    });
  } finally {
    await emitTypingSignal("stop");
  }

  const shouldForceMentionAck = topicType === "discussion"
    && Boolean(inferDecision?.trigger)
    && (mentionTargetedDiscussion || inferDecision?.reason === "discussion_runner_match");

  if (!dispatchProducedOutput && shouldForceMentionAck) {
    params.log?.("warn", `[${params.accountId}] discussion mention produced no visible output (model empty/NO_REPLY)`);
  }

  if (naturalBridgeEnabled && inboundTaskId) {
    const terminal = new Set(["review", "done", "cancelled", "blocked"]);
    if (!terminal.has(naturalBridgeTaskStatus)) {
      if (!dispatchProducedOutput) {
        params.log?.("info", `[${params.accountId}] natural task status bridge skipped (no output) task=${inboundTaskId}`);
      } else {
        if (naturalBridgeTaskStatus === "doing") {
          if (typeof naturalBridgeDoingAtMs === "number") {
            const elapsedMs = Date.now() - naturalBridgeDoingAtMs;
            const waitMs = Math.max(0, DEFAULT_NATURAL_BRIDGE_MIN_DOING_MS - elapsedMs);
            if (waitMs > 0) {
              await new Promise((resolve) => setTimeout(resolve, waitMs));
            }
          }

          const movedReview = await patchTaskStatus(inboundTaskId, "review");
          if (!movedReview) {
            params.log?.("warn", `[${params.accountId}] natural task status bridge post-dispatch failed task=${inboundTaskId}`);
          }
        }
      }
    }
  }

  return { routed: true };
}

type RecoveryTaskCandidate = {
  id: string;
  status: string;
  runnerAgentId?: string;
  ownerAgentId?: string;
  updatedAt?: string;
};

function parseRecoveryTaskCandidates(raw: unknown): RecoveryTaskCandidate[] {
  const payload = asRecord(raw);
  const dataCandidate = asRecord(payload?.data);

  const source = Array.isArray(raw)
    ? raw
    : Array.isArray(payload?.tasks)
      ? payload.tasks
      : Array.isArray(payload?.items)
        ? payload.items
        : Array.isArray(dataCandidate?.tasks)
          ? dataCandidate.tasks
          : Array.isArray(dataCandidate?.items)
            ? dataCandidate.items
            : [];

  const parsed: RecoveryTaskCandidate[] = [];
  for (const item of source) {
    const record = asRecord(item);
    if (!record) continue;

    const id = toOptionalString(record.id);
    const status = toOptionalString(record.status);
    if (!id || !status) continue;

    parsed.push({
      id,
      status: status.toLowerCase(),
      runnerAgentId: toOptionalString(record.runner_agent_id),
      ownerAgentId: toOptionalString(record.owner_agent_id),
      updatedAt: toOptionalString(record.updated_at) ?? toOptionalString(record.created_at),
    });
  }

  return parsed;
}

function parseIsoMs(input?: string): number | undefined {
  if (!input) return undefined;
  const t = Date.parse(input);
  return Number.isFinite(t) ? t : undefined;
}

async function startGatewayAccount(ctx: GatewayStartContext): Promise<void> {
  const log = (level: "debug" | "info" | "warn" | "error", msg: string, data?: unknown): void => {
    if (level === "debug") ctx.log?.debug?.(msg);
    else if (level === "info") ctx.log?.info?.(msg);
    else if (level === "warn") ctx.log?.warn?.(msg);
    else ctx.log?.error?.(data ? `${msg} ${String(data)}` : msg);
  };

  let activeClient: WTTCloudClient | undefined;
  let pollTimer: ReturnType<typeof setInterval> | undefined;
  let recoveryTimer: ReturnType<typeof setInterval> | undefined;
  let pollInFlight = false;
  let recoveryInFlight = false;

  const pollIntervalMs = toPositiveInt(ctx.account.config.inboundPollIntervalMs, DEFAULT_INBOUND_POLL_INTERVAL_MS);
  const pollLimit = toPositiveInt(ctx.account.config.inboundPollLimit, DEFAULT_INBOUND_POLL_LIMIT);
  const recoveryIntervalMs = DEFAULT_TASK_RECOVERY_INTERVAL_MS;
  const recoveryLookbackMs = DEFAULT_TASK_RECOVERY_LOOKBACK_MS;
  const recoverySeenAt = new Map<string, number>();
  const todoRecheckTimers = new Map<string, ReturnType<typeof setTimeout>>();

  const inboundRelay = createInboundMessageRelay({
    cfg: ctx.cfg,
    accountId: ctx.accountId,
    account: ctx.account,
    getLatestAccount: () => {
      const client = getClient(ctx.accountId);
      return client ? client.getAccount() : ctx.account;
    },
    channelRuntime: ctx.channelRuntime,
    decryptContent: async (content: string) => {
      const runtimeClient = getClient(ctx.accountId);
      if (!runtimeClient) return content;
      return runtimeClient.decryptMessage(content);
    },
    typingSignal: async ({ topicId, state, ttlMs }) => {
      const runtimeClient = getClient(ctx.accountId);
      if (!runtimeClient || !runtimeClient.connected) return;
      await runtimeClient.typing(topicId, state, ttlMs ?? 6000);
    },
    log,
    dedupWindowMs: ctx.account.config.inboundDedupWindowMs,
    dedupMaxEntries: ctx.account.config.inboundDedupMaxEntries,
  });

  const scheduleTodoRecheck = (taskId: string, delayMs = 5000): void => {
    if (todoRecheckTimers.has(taskId)) return;

    const timer = setTimeout(async () => {
      todoRecheckTimers.delete(taskId);
      try {
        if (ctx.abortSignal.aborted || !ctx.channelRuntime) return;

        const accountContext = resolveCommandAccountContext(ctx.accountId, ctx.cfg);
        const account = normalizeAccountContext(ctx.accountId, accountContext);
        if (!account.hasToken || !account.agentId) return;

        const detailResp = await fetch(`${account.cloudUrl.replace(/\/$/, "")}/tasks/${encodeURIComponent(taskId)}`, {
          method: "GET",
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${account.token}`,
            "X-Agent-Token": account.token,
          },
        });
        if (!detailResp.ok) return;

        const detailPayload = await detailResp.json() as Record<string, unknown>;
        const liveStatus = String(detailPayload.status ?? "").trim().toLowerCase();
        const TERMINAL_STATUSES = new Set(["review", "done", "cancelled", "blocked"]);
        if (TERMINAL_STATUSES.has(liveStatus)) return;

        const taskExecutorScope = (ctx.account.config.taskExecutorScope ?? "all").toLowerCase();
        if (taskExecutorScope === "pipeline_only") {
          const liveTaskType = String(detailPayload.task_type ?? detailPayload.taskType ?? "").trim().toLowerCase();
          const liveExecMode = String(detailPayload.exec_mode ?? detailPayload.execMode ?? "").trim().toLowerCase();
          const liveTaskMode = String(detailPayload.task_mode ?? detailPayload.taskMode ?? "").trim().toLowerCase();
          const livePipelineId = detailPayload.pipeline_id ?? detailPayload.pipelineId ?? "";

          const isPipelineTask = [liveTaskType, liveExecMode, liveTaskMode].includes("pipeline") || hasMeaningfulPipelineId(livePipelineId);
          if (!isPipelineTask) {
            log("info", `[${ctx.accountId}] task_status todo recheck skipped non-pipeline task=${taskId}`);
            return;
          }
        }

        const runtimeHooks = createTaskInferenceRuntimeHooks({
          cfg: ctx.cfg,
          accountId: ctx.accountId,
          account: accountContext,
          channelRuntime: ctx.channelRuntime,
        });

        const runResult = await executeTaskRunById({
          taskId,
          ctx: {
            accountId: ctx.accountId,
            account,
            client: activeClient,
            clientConnected: Boolean(activeClient?.connected),
            fetchImpl: fetch,
            runtimeHooks,
          },
          account,
          note: "triggered by task_status todo recheck",
          heartbeatSeconds: 60,
          publishHeartbeatToStream: true,
        });

        const enqueue = runResult.enqueueResult;
        const detail = enqueue.deduplicated
          ? `idempotency=${enqueue.idempotency.decision} duplicate_state=${enqueue.idempotency.duplicateState ?? "-"}`
          : `idempotency=${enqueue.idempotency.decision} final_status=${enqueue.finalStatus} transition=${enqueue.transitionApplied}`;

        log("info", `[${ctx.accountId}] task_status todo recheck dispatched task=${taskId} ${detail}`);
      } catch (err) {
        log("warn", `[${ctx.accountId}] task_status todo recheck failed task=${taskId}`, err);
      }
    }, delayMs);

    todoRecheckTimers.set(taskId, timer);
  };

  const taskStatusHandler = createTaskStatusEventHandler({
    runTask: async ({ taskId, status, event }) => {
      if (!ctx.channelRuntime) {
        throw new Error("channel_runtime_unavailable");
      }

      const accountContext = resolveCommandAccountContext(ctx.accountId, ctx.cfg);
      const account = normalizeAccountContext(ctx.accountId, accountContext);
      if (!account.hasToken) {
        throw new Error("missing_account_token");
      }

      const taskExecutorScope = (ctx.account.config.taskExecutorScope ?? "all").toLowerCase();
      let liveTaskType = "";
      let liveExecMode = "";
      let liveTaskMode = "";
      let livePipelineId = "";

      // Guard: verify live task status before dispatching run from WS task_status events.
      // - todo: actionable if still todo/doing; terminal statuses are skipped.
      // - doing: only actionable when live status is still doing (avoid stale doing replay after review/done).
      if (status === "todo" || status === "doing") {
        const TERMINAL_STATUSES = new Set(["review", "done", "cancelled", "blocked"]);
        try {
          const detailResp = await fetch(`${account.cloudUrl.replace(/\/$/, "")}/tasks/${encodeURIComponent(taskId)}`, {
            method: "GET",
            headers: {
              Accept: "application/json",
              Authorization: `Bearer ${account.token}`,
              "X-Agent-Token": account.token,
            },
          });

          if (!detailResp.ok) {
            if (status === "todo") {
              scheduleTodoRecheck(taskId);
              return {
                deduplicated: true,
                detail: `skip_todo_detail_fetch_failed:http_${detailResp.status}`,
              };
            }

            return {
              deduplicated: true,
              detail: `skip_doing_detail_fetch_failed:http_${detailResp.status}`,
            };
          }

          const detailPayload = await detailResp.json() as Record<string, unknown>;
          liveTaskType = String(detailPayload.task_type ?? detailPayload.taskType ?? "").trim().toLowerCase();
          liveExecMode = String(detailPayload.exec_mode ?? detailPayload.execMode ?? "").trim().toLowerCase();
          liveTaskMode = String(detailPayload.task_mode ?? detailPayload.taskMode ?? "").trim().toLowerCase();
          livePipelineId = String(detailPayload.pipeline_id ?? detailPayload.pipelineId ?? "").trim();
          const liveStatus = String(detailPayload.status ?? "").trim().toLowerCase();
          if (TERMINAL_STATUSES.has(liveStatus)) {
            // Pipeline task events can briefly replay stale blocked before converging to todo/doing.
            // For TODO events, schedule a delayed recheck to avoid one-shot deadlocks.
            if (status === "todo") {
              scheduleTodoRecheck(taskId, 6000);
              return {
                deduplicated: true,
                detail: `skip_${status}_live_status_terminal:${liveStatus}_recheck_scheduled`,
              };
            }

            return {
              deduplicated: true,
              detail: `skip_${status}_live_status_terminal:${liveStatus}`,
            };
          }

          if (status === "doing" && liveStatus !== "doing") {
            return {
              deduplicated: true,
              detail: `skip_doing_live_status_mismatch:${liveStatus || "unknown"}`,
            };
          }
        } catch (err) {
          // On fetch error, still proceed — executor has its own idempotency guards.
          const msg = err instanceof Error ? err.message : String(err);
          log("warn", `[${ctx.accountId}] task_status ${status} detail fetch error task=${taskId}: ${msg}`);
        }
      }

      if (taskExecutorScope === "pipeline_only") {
        const eventTaskType = String(event.task_type ?? "").trim().toLowerCase();
        const eventExecMode = String(event.exec_mode ?? "").trim().toLowerCase();
        const pipelineHints = [liveTaskType, liveExecMode, liveTaskMode, eventTaskType, eventExecMode];
        const isPipelineTask = pipelineHints.includes("pipeline") || hasMeaningfulPipelineId(livePipelineId);

        if (!isPipelineTask) {
          const hint = (pipelineHints.find(Boolean) || "unknown");
          return {
            deduplicated: true,
            detail: `skip_non_pipeline_task_type:${hint}`,
          };
        }
      }

      const runtimeHooks = createTaskInferenceRuntimeHooks({
        cfg: ctx.cfg,
        accountId: ctx.accountId,
        account: accountContext,
        channelRuntime: ctx.channelRuntime,
        typingSignal: async ({ topicId, state, ttlMs }) => {
          if (!activeClient?.connected) return;
          await activeClient.typing(topicId, state, ttlMs ?? 6000);
        },
      });

      if (!runtimeHooks?.dispatchTaskInference) {
        throw new Error("runtime_hook_unavailable");
      }

      if (!activeClient?.connected) {
        throw new Error("wtt_client_disconnected");
      }

      const runResult = await executeTaskRunById({
        taskId,
        ctx: {
          accountId: ctx.accountId,
          account: accountContext,
          clientConnected: activeClient.connected,
          client: activeClient,
          runtimeHooks,
        },
        account,
        note: `triggered by task_status (${status})`,
        heartbeatSeconds: 60,
        publishHeartbeatToStream: true,
      });

      const enqueue = runResult.enqueueResult;
      const detail = enqueue.deduplicated
        ? `idempotency=${enqueue.idempotency.decision} duplicate_state=${enqueue.idempotency.duplicateState ?? "-"}`
        : `idempotency=${enqueue.idempotency.decision} final_status=${enqueue.finalStatus} transition=${enqueue.transitionApplied}`;

      return {
        deduplicated: enqueue.deduplicated,
        detail,
      };
    },
  });

  const runPollCatchup = async (): Promise<void> => {
    if (ctx.abortSignal.aborted || pollInFlight) return;
    if (!activeClient?.connected) return;

    pollInFlight = true;
    try {
      const raw = await activeClient.poll(pollLimit);
      await inboundRelay.handlePollResult(raw);
    } catch (err) {
      log("warn", `[${ctx.accountId}] inbound poll catch-up failed`, err);
    } finally {
      pollInFlight = false;
    }
  };

  const runTaskRecoverySweep = async (): Promise<void> => {
    if (ctx.abortSignal.aborted || recoveryInFlight) return;
    if (!activeClient?.connected) return;
    if (!ctx.channelRuntime) return;

    const accountContext = resolveCommandAccountContext(ctx.accountId, ctx.cfg);
    const account = normalizeAccountContext(ctx.accountId, accountContext);
    if (!account.hasToken || !account.agentId) return;

    recoveryInFlight = true;
    try {
      const endpoint = `${account.cloudUrl.replace(/\/$/, "")}/tasks`;
      const response = await fetch(endpoint, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${account.token}`,
          "X-Agent-Token": account.token,
        },
      });

      if (!response.ok) {
        throw new Error(`tasks list failed: HTTP ${response.status}`);
      }

      const payload = await response.json();
      const tasks = parseRecoveryTaskCandidates(payload);
      const nowMs = Date.now();
      const cutoffMs = nowMs - recoveryLookbackMs;

      for (const [key, seenAt] of recoverySeenAt) {
        if (seenAt < cutoffMs) recoverySeenAt.delete(key);
      }

      let scanned = 0;
      let triggered = 0;
      for (const task of tasks) {
        if (task.status !== "doing") continue;
        if (task.runnerAgentId !== account.agentId) continue;

        const updatedAtMs = parseIsoMs(task.updatedAt);
        if (typeof updatedAtMs === "number" && updatedAtMs < cutoffMs) continue;

        scanned += 1;
        const dedupKey = `${task.id}:${task.status}:${task.updatedAt ?? ""}`;
        if (recoverySeenAt.has(dedupKey)) continue;
        recoverySeenAt.set(dedupKey, nowMs);

        triggered += 1;
        const consume = await taskStatusHandler.handle({
          type: "task_status",
          task_id: task.id,
          status: "doing",
        });
        const dedupSource = consume.dedupSource ? ` dedup_source=${consume.dedupSource}` : "";
        const dispatchDetail = consume.dispatch?.detail ? ` detail=${consume.dispatch.detail}` : "";
        log(
          "info",
          `[${ctx.accountId}] recovery task_status consume decision=${consume.decision} task=${consume.taskId || task.id} status=doing reason=${consume.reason}${dedupSource}${dispatchDetail}`,
        );
      }

      if (scanned > 0 || triggered > 0) {
        log("info", `[${ctx.accountId}] recovery sweep scanned=${scanned} triggered=${triggered}`);
      }
    } catch (err) {
      log("warn", `[${ctx.accountId}] task recovery sweep failed`, err);
    } finally {
      recoveryInFlight = false;
    }
  };

  try {
    activeClient = await startWsAccount(ctx.accountId, ctx.account, {
      log,
      onMessage: (_accountId, msg) => {
        void inboundRelay.handlePush(msg).catch((err) => {
          log("error", `[${ctx.accountId}] inbound routing error`, err);
        });
      },
      onTaskStatus: (_accountId, status) => {
        void taskStatusHandler.handle(status)
          .then((consume) => {
            const dedupSource = consume.dedupSource ? ` dedup_source=${consume.dedupSource}` : "";
            const dispatchDetail = consume.dispatch?.detail ? ` detail=${consume.dispatch.detail}` : "";
            log(
              "info",
              `[${ctx.accountId}] task_status consume decision=${consume.decision} task=${consume.taskId || "-"} status=${consume.status} reason=${consume.reason}${dedupSource}${dispatchDetail}`,
            );
          })
          .catch((err) => {
            log("error", `[${ctx.accountId}] task_status handler failed`, err);
          });
      },
    });

    if (pollIntervalMs > 0) {
      log("info", `[${ctx.accountId}] inbound poll catch-up enabled interval=${pollIntervalMs}ms limit=${pollLimit}`);
      void runPollCatchup();
      pollTimer = setInterval(() => {
        void runPollCatchup();
      }, pollIntervalMs);
    }

    if (recoveryIntervalMs > 0) {
      log(
        "info",
        `[${ctx.accountId}] task recovery sweep enabled interval=${recoveryIntervalMs}ms lookback_ms=${recoveryLookbackMs}`,
      );
      void runTaskRecoverySweep();
      recoveryTimer = setInterval(() => {
        void runTaskRecoverySweep();
      }, recoveryIntervalMs);
    }

    await waitForAbort(ctx.abortSignal);
  } finally {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = undefined;
    }

    if (recoveryTimer) {
      clearInterval(recoveryTimer);
      recoveryTimer = undefined;
    }

    for (const timer of todoRecheckTimers.values()) {
      clearTimeout(timer);
    }
    todoRecheckTimers.clear();

    log(
      "info",
      `[${ctx.accountId}] inbound summary push_received=${inboundRelay.stats.pushReceivedCount} poll_fetched=${inboundRelay.stats.pollFetchedCount} routed=${inboundRelay.stats.routedCount} dedup_dropped=${inboundRelay.stats.dedupDroppedCount}`,
    );

    await stopAccount(ctx.accountId);
  }
}

const A2UI_MESSAGE_TOOL_HINTS = [
  "WTT supports action fenced code blocks for interactive UI.",
  "Use ```action JSON blocks with kinds: buttons/confirm/select/input.",
  "Prefer compact button choices over long numbered lists.",
].join("\n");

export const wttPlugin = {
  id: "wtt",
  meta: {
    id: "wtt",
    label: "WTT",
    selectionLabel: "WTT (WebSocket)",
    docsPath: "/channels/wtt",
    docsLabel: "wtt",
    blurb: "WTT real-time topic + p2p channel.",
    aliases: ["want-to-talk"],
    order: 95,
  },
  capabilities: {
    chatTypes: ["direct", "group", "thread"],
    threads: true,
    media: true,
  },
  reload: {
    configPrefixes: ["channels.wtt"],
  },
  config: {
    listAccountIds,
    resolveAccount,
    defaultAccountId: () => DEFAULT_ACCOUNT_ID,
    isConfigured: (account: ResolvedWTTAccount) => account.configured,
    describeAccount: (account: ResolvedWTTAccount) => ({
      accountId: account.accountId,
      name: account.name,
      enabled: account.enabled,
      configured: account.configured,
      cloudUrl: account.cloudUrl,
    }),
  },
  gateway: {
    startAccount: startGatewayAccount,
    stopAccount: async (ctx: { accountId: string }) => {
      await stopAccount(ctx.accountId);
    },
  },
  outbound: {
    deliveryMode: "direct",
    textChunkLimit: 4000,
    resolveTarget: ({ to }: { to: string }) => to,
    sendText,
    sendMedia,
  },
  agentPrompt: {
    messageToolHints: () => [A2UI_MESSAGE_TOOL_HINTS],
  },
  hooks: {
    register: registerHook,
    runBefore: (ctx: Parameters<HookFn>[0]) => runHooks("before", ctx),
    runAfter: (ctx: Parameters<HookFn>[0]) => runHooks("after", ctx),
  },
  getClient,
};
