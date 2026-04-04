import { Type } from '@sinclair/typebox';
import type { LeadDB } from '../db/connection.js';
import type { Lead } from '../types/index.js';
import { esc } from '../utils/validation.js';

export const definition = {
  name: 'lead_list',
  label: 'List Leads',
  description: 'List leads with optional stage filter. Returns summary view. Supports limit/offset pagination.',
  parameters: Type.Object({
    stage: Type.Optional(Type.String({ description: 'Filter by stage.' })),
    limit: Type.Optional(Type.Number({ description: 'Max results (default 20).', minimum: 1, maximum: 100 })),
    offset: Type.Optional(Type.Number({ description: 'Skip N results (default 0).', minimum: 0 })),
  }),
};

export async function execute(db: LeadDB, _config: any, params: any) {
  const where = params.stage ? `stage = '${esc(params.stage)}'` : undefined;
  const all = await db.queryLeads(where);

  // Sort by updatedAt desc
  all.sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));

  const offset = params.offset ?? 0;
  const limit = params.limit ?? 20;
  const page = all.slice(offset, offset + limit);

  return jsonResult({
    total: all.length,
    offset,
    limit,
    leads: page.map(summarize),
  });
}

function summarize(l: Lead) {
  return {
    id: l.id,
    name: l.name,
    company: l.company,
    stage: l.stage,
    product: l.product,
    estimatedValue: l.estimatedValue,
    nextAction: l.nextAction,
    nextActionDate: l.nextActionDate,
  };
}

function textResult(text: string) {
  return { content: [{ type: 'text' as const, text }] };
}

function jsonResult(data: any) {
  return textResult(JSON.stringify(data, null, 2));
}
