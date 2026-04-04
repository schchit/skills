import { Type } from '@sinclair/typebox';
import type { LeadDB } from '../db/connection.js';
import type { Lead } from '../types/index.js';

export const definition = {
  name: 'lead_export',
  label: 'Export Pipeline',
  description: 'Export pipeline data as JSON or markdown table for weekly reports.',
  parameters: Type.Object({
    format: Type.Optional(Type.String({ description: 'Output format: "json" or "markdown" (default: markdown).' })),
    stage: Type.Optional(Type.String({ description: 'Filter by stage.' })),
  }),
};

export async function execute(db: LeadDB, _config: any, params: any) {
  const where = params.stage ? `stage = '${esc(params.stage)}'` : undefined;
  const leads = await db.queryLeads(where);
  leads.sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));

  const format = params.format ?? 'markdown';

  if (format === 'json') {
    return jsonResult(leads.map(exportLead));
  }

  // Markdown table
  const header = '| Name | Company | Stage | Product | Est. Value | Next Action | Due |\n|------|---------|-------|---------|-----------|-------------|-----|';
  const rows = leads.map(l =>
    `| ${l.name} | ${l.company ?? '-'} | ${l.stage} | ${l.product ?? '-'} | ${l.estimatedValue != null ? `$${l.estimatedValue}` : '-'} | ${l.nextAction ?? '-'} | ${l.nextActionDate ?? '-'} |`,
  );

  return textResult([header, ...rows].join('\n'));
}

function exportLead(l: Lead) {
  return {
    id: l.id,
    name: l.name,
    email: l.email,
    company: l.company,
    stage: l.stage,
    source: l.source,
    product: l.product,
    estimatedValue: l.estimatedValue,
    actualValue: l.actualValue,
    nextAction: l.nextAction,
    nextActionDate: l.nextActionDate,
    createdAt: l.createdAt,
    updatedAt: l.updatedAt,
    closedAt: l.closedAt,
  };
}

function esc(val: string): string {
  return val.replace(/'/g, "''");
}

function textResult(text: string) {
  return { content: [{ type: 'text' as const, text }] };
}

function jsonResult(data: any) {
  return textResult(JSON.stringify(data, null, 2));
}
