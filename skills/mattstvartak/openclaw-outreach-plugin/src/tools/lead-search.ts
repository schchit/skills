import { Type } from '@sinclair/typebox';
import type { LeadDB } from '../db/connection.js';
import type { Lead } from '../types/index.js';
import { esc } from '../utils/validation.js';
import { today, isOnOrBefore } from '../utils/dates.js';

export const definition = {
  name: 'lead_search',
  label: 'Search Leads',
  description: 'Search leads by stage, source, product, tags, date range, or free-text query. Use the "due" flag to filter leads with nextActionDate <= today.',
  parameters: Type.Object({
    stage: Type.Optional(Type.String({ description: 'Filter by stage.' })),
    source: Type.Optional(Type.String({ description: 'Filter by source.' })),
    product: Type.Optional(Type.String({ description: 'Filter by product.' })),
    tags: Type.Optional(Type.Array(Type.String(), { description: 'Filter by tags (match any).' })),
    query: Type.Optional(Type.String({ description: 'Free-text search against name, company, notes.' })),
    dateFrom: Type.Optional(Type.String({ description: 'Filter leads created on or after this ISO date.' })),
    dateTo: Type.Optional(Type.String({ description: 'Filter leads created on or before this ISO date.' })),
    due: Type.Optional(Type.Boolean({ description: 'If true, only return leads where nextActionDate <= today.' })),
    limit: Type.Optional(Type.Number({ description: 'Max results (default 50).', minimum: 1, maximum: 200 })),
  }),
};

export async function execute(db: LeadDB, _config: any, params: any) {
  const conditions: string[] = [];

  if (params.stage) conditions.push(`stage = '${esc(params.stage)}'`);
  if (params.source) conditions.push(`source = '${esc(params.source)}'`);
  if (params.product) conditions.push(`product = '${esc(params.product)}'`);
  if (params.dateFrom) conditions.push(`created_at >= '${esc(params.dateFrom)}'`);
  if (params.dateTo) conditions.push(`created_at <= '${esc(params.dateTo)}'`);

  const where = conditions.length > 0 ? conditions.join(' AND ') : undefined;
  let leads = await db.queryLeads(where);

  // Tag filtering (stored as JSON string, filter in-app)
  if (params.tags && params.tags.length > 0) {
    const searchTags = new Set(params.tags.map((t: string) => t.toLowerCase()));
    leads = leads.filter(l => l.tags.some(t => searchTags.has(t.toLowerCase())));
  }

  // Free-text search
  if (params.query) {
    const q = params.query.toLowerCase();
    leads = leads.filter(l =>
      l.name.toLowerCase().includes(q) ||
      (l.company?.toLowerCase().includes(q)) ||
      l.notes.toLowerCase().includes(q),
    );
  }

  // Due filter
  if (params.due) {
    const t = today();
    leads = leads.filter(l => l.nextActionDate && isOnOrBefore(l.nextActionDate, t));
  }

  // Sort by updatedAt desc
  leads.sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));

  const limit = params.limit ?? 50;
  leads = leads.slice(0, limit);

  return jsonResult({
    count: leads.length,
    leads: leads.map(summarize),
  });
}

function summarize(l: Lead) {
  return {
    id: l.id,
    name: l.name,
    company: l.company,
    stage: l.stage,
    source: l.source,
    product: l.product,
    estimatedValue: l.estimatedValue,
    nextAction: l.nextAction,
    nextActionDate: l.nextActionDate,
    updatedAt: l.updatedAt,
  };
}

function textResult(text: string) {
  return { content: [{ type: 'text' as const, text }] };
}

function jsonResult(data: any) {
  return textResult(JSON.stringify(data, null, 2));
}
