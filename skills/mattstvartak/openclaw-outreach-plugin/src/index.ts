import { homedir } from 'node:os';
import { join } from 'node:path';
import { LeadDB } from './db/connection.js';
import * as leadCreate from './tools/lead-create.js';
import * as leadUpdate from './tools/lead-update.js';
import * as leadStage from './tools/lead-stage.js';
import * as leadSearch from './tools/lead-search.js';
import * as leadList from './tools/lead-list.js';
import * as leadContact from './tools/lead-contact.js';
import * as leadFollowup from './tools/lead-followup.js';
import * as leadStats from './tools/lead-stats.js';
import * as leadDue from './tools/lead-due.js';
import * as leadExport from './tools/lead-export.js';
import type { OutreachConfig } from './types/index.js';

// -- Config --

function resolveDataDir(raw: string): string {
  if (raw.startsWith('~')) return join(homedir(), raw.slice(1));
  return raw;
}

function loadConfig(pluginConfig: Record<string, any>): OutreachConfig {
  return {
    dataDir: resolveDataDir(pluginConfig.dataDir ?? '~/.openclaw/openclaw-outreach-plugin'),
    maxLeads: pluginConfig.maxLeads ?? 500,
    overdueAlertDays: pluginConfig.overdueAlertDays ?? 3,
  };
}

// -- Lazy singleton --

let _db: LeadDB | null = null;
let _dbReady: Promise<void> | null = null;

async function ensureDB(config: OutreachConfig): Promise<LeadDB> {
  if (!_db) {
    _db = new LeadDB(config.dataDir);
    _dbReady = _db.ensureReady();
  }
  await _dbReady;
  return _db;
}

// -- Helpers --

function textResult(text: string) {
  return { content: [{ type: 'text' as const, text }] };
}

// -- Tool registry --

const tools = [
  leadCreate,
  leadUpdate,
  leadStage,
  leadSearch,
  leadList,
  leadContact,
  leadFollowup,
  leadStats,
  leadDue,
  leadExport,
];

// -- Plugin --

const plugin = {
  id: 'openclaw-outreach-plugin',
  name: 'Outreach Pipeline',
  description: 'Lead tracking and outreach pipeline for autonomous sales. Manages leads through identification, contact, negotiation, and conversion.',

  register(api: any) {
    const pluginConfig = api.pluginConfig ?? {};
    const config = loadConfig(pluginConfig);

    for (const tool of tools) {
      api.registerTool({
        name: tool.definition.name,
        label: tool.definition.label,
        description: tool.definition.description,
        parameters: tool.definition.parameters,
        async execute(_id: string, params: any) {
          try {
            const db = await ensureDB(config);
            return await tool.execute(db, config, params);
          } catch (err: any) {
            return textResult(`Error in ${tool.definition.name}: ${err.message}`);
          }
        },
      }, { name: tool.definition.name });
    }

    // -- Prompt guidance --

    const OUTREACH_GUIDANCE = [
      '## Outreach Pipeline',
      'At session start, call lead_due to check for overdue follow-ups before doing anything else.',
      'After sending any outreach, call lead_contact to log it and lead_followup to schedule the next action.',
      'After receiving a reply, update the stage with lead_stage and log the event with lead_contact.',
      'At end of week, call lead_stats and lead_export for the Notion report.',
    ].join('\n');

    api.on('before_prompt_build', async () => ({
      prependSystemContext: OUTREACH_GUIDANCE,
    }));

    api.logger?.info('Outreach Pipeline plugin registered');
  },
};

export default plugin;
