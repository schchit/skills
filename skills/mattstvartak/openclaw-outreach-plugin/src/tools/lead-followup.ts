import { Type } from '@sinclair/typebox';
import type { LeadDB } from '../db/connection.js';
import { now } from '../utils/dates.js';

export const definition = {
  name: 'lead_followup',
  label: 'Set Follow-up',
  description: 'Set or update the nextAction and nextActionDate on a lead. Call this after every interaction to schedule what happens next.',
  parameters: Type.Object({
    id: Type.String({ description: 'Lead ID.' }),
    nextAction: Type.String({ description: 'What to do next.' }),
    nextActionDate: Type.String({ description: 'ISO date (YYYY-MM-DD) for next follow-up.' }),
  }),
};

export async function execute(db: LeadDB, _config: any, params: any) {
  const lead = await db.getLead(params.id);
  if (!lead) return textResult(`Error: lead "${params.id}" not found.`);

  await db.updateLead(params.id, {
    nextAction: params.nextAction,
    nextActionDate: params.nextActionDate,
    updatedAt: now(),
  });

  return jsonResult({
    id: lead.id,
    name: lead.name,
    nextAction: params.nextAction,
    nextActionDate: params.nextActionDate,
  });
}

function textResult(text: string) {
  return { content: [{ type: 'text' as const, text }] };
}

function jsonResult(data: any) {
  return textResult(JSON.stringify(data, null, 2));
}
