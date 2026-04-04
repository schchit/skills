import * as lancedb from '@lancedb/lancedb';
import { existsSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { LEAD_SEED, CONTACT_EVENT_SEED } from './schema.js';
import type { Lead, ContactEvent } from '../types/index.js';
import { esc } from '../utils/validation.js';

export class LeadDB {
  private db!: lancedb.Connection;
  private leads!: lancedb.Table;
  private events!: lancedb.Table;
  private dbPath: string;
  private ready: Promise<void>;

  constructor(dataDir: string) {
    this.dbPath = join(dataDir, 'lance');
    if (!existsSync(dataDir)) mkdirSync(dataDir, { recursive: true });
    this.ready = this.initAsync();
  }

  private async initAsync(): Promise<void> {
    this.db = await lancedb.connect(this.dbPath);
    const tables = await this.db.tableNames();

    if (tables.includes('leads')) {
      this.leads = await this.db.openTable('leads');
    } else {
      this.leads = await this.db.createTable('leads', [LEAD_SEED]);
      await this.leads.delete("id = '__init__'");
    }

    if (tables.includes('contact_events')) {
      this.events = await this.db.openTable('contact_events');
    } else {
      this.events = await this.db.createTable('contact_events', [CONTACT_EVENT_SEED]);
      await this.events.delete("id = '__init__'");
    }
  }

  async ensureReady(): Promise<void> {
    await this.ready;
  }

  // -- Lead CRUD --

  async insertLead(lead: Lead): Promise<void> {
    await this.leads.add([leadToRow(lead)]);
  }

  async getLead(id: string): Promise<Lead | null> {
    const rows = await this.leads.query()
      .where(`id = '${esc(id)}'`)
      .limit(1)
      .toArray();
    if (rows.length === 0) return null;
    const lead = rowToLead(rows[0]);
    lead.contactHistory = await this.getEvents(id);
    return lead;
  }

  async updateLead(id: string, updates: Partial<Lead>): Promise<void> {
    const values: Record<string, any> = {};
    if (updates.name !== undefined) values.name = updates.name;
    if (updates.email !== undefined) values.email = updates.email;
    if (updates.company !== undefined) values.company = updates.company ?? '';
    if (updates.source !== undefined) values.source = updates.source;
    if (updates.sourceUrl !== undefined) values.source_url = updates.sourceUrl ?? '';
    if (updates.stage !== undefined) values.stage = updates.stage;
    if (updates.product !== undefined) values.product = updates.product ?? '';
    if (updates.estimatedValue !== undefined) values.estimated_value = updates.estimatedValue ?? 0;
    if (updates.actualValue !== undefined) values.actual_value = updates.actualValue ?? 0;
    if (updates.notes !== undefined) values.notes = updates.notes;
    if (updates.tags !== undefined) values.tags = JSON.stringify(updates.tags);
    if (updates.nextAction !== undefined) values.next_action = updates.nextAction ?? '';
    if (updates.nextActionDate !== undefined) values.next_action_date = updates.nextActionDate ?? '';
    if (updates.updatedAt !== undefined) values.updated_at = updates.updatedAt;
    if (updates.closedAt !== undefined) values.closed_at = updates.closedAt ?? '';
    if (Object.keys(values).length === 0) return;
    await this.leads.update({ where: `id = '${esc(id)}'`, values });
  }

  async deleteLead(id: string): Promise<void> {
    await this.leads.delete(`id = '${esc(id)}'`);
    await this.events.delete(`lead_id = '${esc(id)}'`);
  }

  async queryLeads(where?: string): Promise<Lead[]> {
    let q = this.leads.query();
    if (where) q = q.where(where);
    const rows = await q.toArray();
    return rows.map(rowToLead);
  }

  async countLeads(): Promise<number> {
    return await this.leads.countRows();
  }

  // -- Contact Events --

  async insertEvent(event: ContactEvent): Promise<void> {
    await this.events.add([eventToRow(event)]);
  }

  async getEvents(leadId: string): Promise<ContactEvent[]> {
    const rows = await this.events.query()
      .where(`lead_id = '${esc(leadId)}'`)
      .toArray();
    return rows.map(rowToEvent);
  }
}

// -- Row mapping --

function leadToRow(lead: Lead): Record<string, any> {
  return {
    id: lead.id,
    name: lead.name,
    email: lead.email,
    company: lead.company ?? '',
    source: lead.source,
    source_url: lead.sourceUrl ?? '',
    stage: lead.stage,
    product: lead.product ?? '',
    estimated_value: lead.estimatedValue ?? 0,
    actual_value: lead.actualValue ?? 0,
    notes: lead.notes,
    tags: JSON.stringify(lead.tags),
    next_action: lead.nextAction ?? '',
    next_action_date: lead.nextActionDate ?? '',
    contact_history: '[]', // stored in separate table
    created_at: lead.createdAt,
    updated_at: lead.updatedAt,
    closed_at: lead.closedAt ?? '',
  };
}

function rowToLead(row: any): Lead {
  return {
    id: row.id,
    name: row.name,
    email: row.email || '',
    company: row.company || null,
    source: row.source,
    sourceUrl: row.source_url || null,
    stage: row.stage,
    product: row.product || null,
    estimatedValue: row.estimated_value || null,
    actualValue: row.actual_value || null,
    notes: row.notes || '',
    tags: JSON.parse(row.tags || '[]'),
    nextAction: row.next_action || null,
    nextActionDate: row.next_action_date || null,
    contactHistory: [],
    createdAt: row.created_at,
    updatedAt: row.updated_at,
    closedAt: row.closed_at || null,
  };
}

function eventToRow(event: ContactEvent): Record<string, any> {
  return {
    id: event.id,
    lead_id: event.leadId,
    type: event.type,
    channel: event.channel,
    summary: event.summary,
    content: event.content ?? '',
    sent_at: event.sentAt,
    metadata: JSON.stringify(event.metadata),
  };
}

function rowToEvent(row: any): ContactEvent {
  return {
    id: row.id,
    leadId: row.lead_id,
    type: row.type,
    channel: row.channel,
    summary: row.summary,
    content: row.content || null,
    sentAt: row.sent_at,
    metadata: JSON.parse(row.metadata || '{}'),
  };
}
