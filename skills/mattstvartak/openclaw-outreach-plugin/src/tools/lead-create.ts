import { Type } from '@sinclair/typebox';
import type { LeadDB } from '../db/connection.js';
import type { OutreachConfig, Lead } from '../types/index.js';
import { newId } from '../utils/uuid.js';
import { now } from '../utils/dates.js';

export const definition = {
  name: 'lead_create',
  label: 'Create Lead',
  description: 'Create a new lead in the outreach pipeline. Required: name, and either email or company. Auto-sets stage to "identified".',
  parameters: Type.Object({
    name: Type.String({ description: 'Lead name (person or handle).' }),
    email: Type.Optional(Type.String({ description: 'Email address.' })),
    company: Type.Optional(Type.String({ description: 'Company or organization.' })),
    source: Type.String({ description: 'Where lead was found: reddit, producthunt, indiehackers, cold_outreach, inbound, etc.' }),
    sourceUrl: Type.Optional(Type.String({ description: 'URL of the post/page where lead was identified.' })),
    product: Type.Optional(Type.String({ description: 'Which product/service this lead is for.' })),
    estimatedValue: Type.Optional(Type.Number({ description: 'Estimated deal value in USD.' })),
    notes: Type.Optional(Type.String({ description: 'Initial notes about the lead.' })),
    tags: Type.Optional(Type.Array(Type.String(), { description: 'Tags for categorization.' })),
    nextAction: Type.Optional(Type.String({ description: 'What to do next.' })),
    nextActionDate: Type.Optional(Type.String({ description: 'ISO date for next follow-up.' })),
  }),
};

export async function execute(
  db: LeadDB,
  config: OutreachConfig,
  params: any,
): Promise<{ content: Array<{ type: 'text'; text: string }> }> {
  if (!params.email && !params.company) {
    return textResult('Error: either email or company is required.');
  }

  const count = await db.countLeads();
  if (count >= config.maxLeads) {
    return textResult(`Error: max leads (${config.maxLeads}) reached. Close or remove existing leads first.`);
  }

  const timestamp = now();
  const lead: Lead = {
    id: newId(),
    name: params.name,
    email: params.email ?? '',
    company: params.company ?? null,
    source: params.source,
    sourceUrl: params.sourceUrl ?? null,
    stage: 'identified',
    product: params.product ?? null,
    estimatedValue: params.estimatedValue ?? null,
    actualValue: null,
    notes: params.notes ?? '',
    tags: params.tags ?? [],
    nextAction: params.nextAction ?? null,
    nextActionDate: params.nextActionDate ?? null,
    contactHistory: [],
    createdAt: timestamp,
    updatedAt: timestamp,
    closedAt: null,
  };

  await db.insertLead(lead);

  return jsonResult({
    id: lead.id,
    name: lead.name,
    stage: lead.stage,
    source: lead.source,
    createdAt: lead.createdAt,
  });
}

function textResult(text: string) {
  return { content: [{ type: 'text' as const, text }] };
}

function jsonResult(data: any) {
  return textResult(JSON.stringify(data, null, 2));
}
