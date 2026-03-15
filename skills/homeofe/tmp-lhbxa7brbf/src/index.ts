import pluginManifest from "../openclaw.plugin.json";
export { ISPConfigError, ISPConfigErrorCode, normalizeError } from "./errors";
import { createTools } from "./tools";
import { ISPConfigPluginConfig, JsonMap } from "./types";

export interface OpenClawRuntimeLike {
  registerTool: (name: string, definition: { description: string; parameters?: Record<string, unknown>; run: (params: JsonMap) => Promise<unknown> }) => void;
}

function ensureConfig(config: Partial<ISPConfigPluginConfig>): ISPConfigPluginConfig {
  if (!config.apiUrl || !config.username || !config.password) {
    throw new Error("Missing required config: apiUrl, username, password");
  }

  return {
    apiUrl: config.apiUrl,
    username: config.username,
    password: config.password,
    serverId: config.serverId ?? 1,
    defaultServerIp: config.defaultServerIp,
    readOnly: config.readOnly ?? false,
    allowedOperations: config.allowedOperations ?? [],
    verifySsl: config.verifySsl ?? true,
    timeoutMs: config.timeoutMs,
  };
}

export interface BoundTool {
  name: string;
  description: string;
  parameters?: {
    type: "object";
    properties: Record<string, unknown>;
    required?: string[];
  };
  run: (params: JsonMap) => Promise<unknown>;
}

export function buildToolset(config: Partial<ISPConfigPluginConfig>): BoundTool[] {
  const safeConfig = ensureConfig(config);
  const context = { config: safeConfig };
  return createTools().map((tool) => ({
    name: tool.name,
    description: tool.description,
    parameters: tool.parameters ?? { type: "object" as const, properties: {} },
    run: (params: JsonMap) => tool.run(params, context),
  }));
}

export function registerAllTools(runtime: OpenClawRuntimeLike, config: Partial<ISPConfigPluginConfig>): void {
  const tools = buildToolset(config);
  for (const tool of tools) {
    runtime.registerTool(tool.name, {
      description: tool.description,
      parameters: tool.parameters,
      run: (params: JsonMap) => tool.run(params),
    });
  }
}

// OpenClaw PluginApi adapter
function registerViaApi(api: any): void {
  const config = (api.pluginConfig ?? {}) as Partial<ISPConfigPluginConfig>;
  const tools = buildToolset(config);
  for (const tool of tools) {
    api.registerTool({
      name: tool.name,
      description: tool.description,
      parameters: tool.parameters,
      execute: (params: JsonMap) => tool.run(params),
    });
  }

  // Command: /ispconfig — show plugin help
  api.registerCommand({
    name: "ispconfig",
    description: "Show ISPConfig plugin help and list of available tools.",
    usage: "/ispconfig",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const rawUrl: string = (config.apiUrl ?? "").trim();
      // Extract hostname only — never expose credentials
      let displayHost = "(not configured)";
      try {
        if (rawUrl) {
          displayHost = new URL(rawUrl).hostname;
        }
      } catch {
        displayHost = rawUrl.replace(/^https?:\/\//, "").split("/")[0] ?? rawUrl;
      }

      const version: string = (pluginManifest as { version?: string }).version ?? "0.2.0";

      const text = [
        `🖥️ *ISPConfig Plugin*`,
        `Version ${version} | Connected to ${displayHost}`,
        ``,
        `📋 *Read Commands*`,
        `• isp_system_info — Server-Info`,
        `• isp_client_list — Alle Clients`,
        `• isp_client_get — Client Details (client_id)`,
        `• isp_sites_list — Alle Websites`,
        `• isp_site_get — Site Details (site_id)`,
        `• isp_domains_list — Alle Domains`,
        `• isp_dns_zone_list — DNS Zonen`,
        `• isp_dns_record_list — DNS Records (zone_id)`,
        `• isp_mail_domain_list — Mail-Domains`,
        `• isp_mail_user_list — Mail-User`,
        `• isp_db_list — Datenbanken`,
        `• isp_cron_list — Cron Jobs`,
        `• isp_ssl_status — SSL/LE Status`,
        `• isp_quota_check — Quota (client_id)`,
        `• isp_methods_list — Verfügbare API-Methoden`,
        ``,
        `✏️ *Write Commands*`,
        `• isp_client_add — Client anlegen`,
        `• isp_site_add — Website anlegen`,
        `• isp_dns_zone_add — DNS Zone`,
        `• isp_dns_record_add — DNS Record (type: A/AAAA/MX/TXT/CNAME)`,
        `• isp_dns_record_delete — DNS Record löschen`,
        `• isp_mail_domain_add — Mail-Domain`,
        `• isp_mail_user_add / _delete — Mail-User`,
        `• isp_db_add / isp_db_user_add — Datenbank`,
        `• isp_ftp_user_add — FTP User`,
        `• isp_shell_user_add — Shell User`,
        `• isp_cron_add — Cron Job`,
        ``,
        `🚀 *Provisioning*`,
        `• isp_provision_site — Alles auf einmal (domain, clientName, clientEmail)`,
      ].join("\n");

      return { text };
    },
  });
}

const plugin = {
  manifest: pluginManifest,
  register: registerViaApi,
};

export default plugin;
