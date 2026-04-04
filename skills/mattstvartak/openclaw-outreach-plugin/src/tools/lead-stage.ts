import { Type } from '@sinclair/typebox';
import type { LeadDB } from '../db/connection.js';
import type { LeadStage } from '../types/index.js';
import { now } from '../utils/dates.js';
import { validateTransition, isClosedStage } from '../utils/validation.js';

export const definition = {
  name: 'lead_stage',
  label: 'Move Lead Stage',
  description: 'Move a lead to a new pipeline stage. Validates transitions. Sets closedAt when moving to won/lost/dead.',
  parameters: Type.Object({
    id: Type.String({ description: 'Lead ID.' }),
    stage: Type.String({ description: 'Target stage: identified, researched, contacted, replied, negotiating, won, lost, dead.' }),
  }),
};

export async function execute(db: LeadDB, _config: any, params: any) {
  const lead = await db.getLead(params.id);
  if (!lead) return textResult(`Error: lead "${params.id}" not found.`);

  const target = params.stage as LeadStage;
  const error = validateTransition(lead.stage, target);
  if (error) return textResult(`Error: ${error}`);

  const timestamp = now();
  const updates: Record<string, any> = {
    stage: target,
    updatedAt: timestamp,
  };

  if (isClosedStage(target)) {
    updates.closedAt = timestamp;
  }

  // Re-opening from lost clears closedAt
  if (lead.stage === 'lost' && target === 'contacted') {
    updates.closedAt = null;
  }

  await db.updateLead(params.id, updates);
  const updated = await db.getLead(params.id);

  return jsonResult({
    id: updated!.id,
    name: updated!.name,
    previousStage: lead.stage,
    stage: updated!.stage,
    closedAt: updated!.closedAt,
  });
}

function textResult(text: string) {
  return { content: [{ type: 'text' as const, text }] };
}

function jsonResult(data: any) {
  return textResult(JSON.stringify(data, null, 2));
}
