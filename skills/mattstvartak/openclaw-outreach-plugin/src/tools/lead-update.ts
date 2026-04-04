import { Type } from '@sinclair/typebox';
import type { LeadDB } from '../db/connection.js';
import { now } from '../utils/dates.js';

export const definition = {
  name: 'lead_update',
  label: 'Update Lead',
  description: 'Update fields on an existing lead by ID. Automatically bumps updatedAt.',
  parameters: Type.Object({
    id: Type.String({ description: 'Lead ID.' }),
    name: Type.Optional(Type.String({ description: 'Updated name.' })),
    email: Type.Optional(Type.String({ description: 'Updated email.' })),
    company: Type.Optional(Type.String({ description: 'Updated company.' })),
    source: Type.Optional(Type.String({ description: 'Updated source.' })),
    sourceUrl: Type.Optional(Type.String({ description: 'Updated source URL.' })),
    product: Type.Optional(Type.String({ description: 'Updated product.' })),
    estimatedValue: Type.Optional(Type.Number({ description: 'Updated estimated value.' })),
    actualValue: Type.Optional(Type.Number({ description: 'Updated actual value.' })),
    notes: Type.Optional(Type.String({ description: 'Updated notes (replaces existing).' })),
    tags: Type.Optional(Type.Array(Type.String(), { description: 'Updated tags (replaces existing).' })),
  }),
};

export async function execute(db: LeadDB, _config: any, params: any) {
  const lead = await db.getLead(params.id);
  if (!lead) return textResult(`Error: lead "${params.id}" not found.`);

  const updates: Record<string, any> = { updatedAt: now() };
  for (const key of ['name', 'email', 'company', 'source', 'sourceUrl', 'product', 'estimatedValue', 'actualValue', 'notes', 'tags']) {
    if (params[key] !== undefined) updates[key] = params[key];
  }

  await db.updateLead(params.id, updates);
  const updated = await db.getLead(params.id);

  return jsonResult({
    id: updated!.id,
    name: updated!.name,
    stage: updated!.stage,
    updatedAt: updated!.updatedAt,
  });
}

function textResult(text: string) {
  return { content: [{ type: 'text' as const, text }] };
}

function jsonResult(data: any) {
  return textResult(JSON.stringify(data, null, 2));
}
