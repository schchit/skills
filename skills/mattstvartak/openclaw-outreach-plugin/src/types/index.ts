export interface ContactEvent {
  id: string;
  leadId: string;
  type:
    | 'email_sent'
    | 'email_received'
    | 'forum_post'
    | 'forum_reply'
    | 'dm_sent'
    | 'dm_received'
    | 'meeting'
    | 'note'
    | 'payment_received';
  channel: string;
  summary: string;
  content: string | null;
  sentAt: string;
  metadata: Record<string, any>;
}

export type LeadStage =
  | 'identified'
  | 'researched'
  | 'contacted'
  | 'replied'
  | 'negotiating'
  | 'won'
  | 'lost'
  | 'dead';

export interface Lead {
  id: string;
  name: string;
  email: string;
  company: string | null;
  source: string;
  sourceUrl: string | null;
  stage: LeadStage;
  product: string | null;
  estimatedValue: number | null;
  actualValue: number | null;
  notes: string;
  tags: string[];
  nextAction: string | null;
  nextActionDate: string | null;
  contactHistory: ContactEvent[];
  createdAt: string;
  updatedAt: string;
  closedAt: string | null;
}

export interface OutreachConfig {
  dataDir: string;
  maxLeads: number;
  overdueAlertDays: number;
}
