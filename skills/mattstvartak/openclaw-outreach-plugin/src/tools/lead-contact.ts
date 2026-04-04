import { Type } from '@sinclair/typebox';
import type { LeadDB } from '../db/connection.js';
import type { ContactEvent } from '../types/index.js';
import { newId } from '../utils/uuid.js';
import { now } from '../utils/dates.js';

export const definition = {
  name: 'lead_contact',
  label: 'Log Contact Event',
  description: 'Log an interaction with a lead: email, forum post, DM, meeting, note, or payment. Appends to contact history.',
  parameters: Type.Object({
    leadId: Type.String({ description: 'Lead ID.' }),
    type: Type.String({ description: 'Event type: email_sent, email_received, forum_post, forum_reply, dm_sent, dm_received, meeting, note, payment_received.' }),
    channel: Type.String({ description: 'Channel: gmail, reddit, discord, twitter, etc.' }),
    summary: Type.String({ description: 'Brief description of the interaction.' }),
    content: Type.Optional(Type.String({ description: 'Full content if available.' })),
    metadata: Type.Optional(Type.String({ description: 'JSON string of extra metadata.' })),
  }),
};

export async function execute(db: LeadDB, _config: any, params: any) {
  const lead = await db.getLead(params.leadId);
  if (!lead) return textResult(`Error: lead "${params.leadId}" not found.`);

  const event: ContactEvent = {
    id: newId(),
    leadId: params.leadId,
    type: params.type,
    channel: params.channel,
    summary: params.summary,
    content: params.content ?? null,
    sentAt: now(),
    metadata: params.metadata ? JSON.parse(params.metadata) : {},
  };

  await db.insertEvent(event);
  await db.updateLead(params.leadId, { updatedAt: now() });

  return jsonResult({
    eventId: event.id,
    leadId: event.leadId,
    type: event.type,
    channel: event.channel,
    summary: event.summary,
    sentAt: event.sentAt,
  });
}

function textResult(text: string) {
  return { content: [{ type: 'text' as const, text }] };
}

function jsonResult(data: any) {
  return textResult(JSON.stringify(data, null, 2));
}
