// LanceDB seed rows for table creation (deleted immediately after).
// LanceDB requires initial data to infer schema.

export const LEAD_SEED = {
  id: '__init__',
  name: '',
  email: '',
  company: '',
  source: '',
  source_url: '',
  stage: 'identified',
  product: '',
  estimated_value: 0,
  actual_value: 0,
  notes: '',
  tags: '[]',
  next_action: '',
  next_action_date: '',
  contact_history: '[]',
  created_at: '',
  updated_at: '',
  closed_at: '',
};

export const CONTACT_EVENT_SEED = {
  id: '__init__',
  lead_id: '',
  type: 'note',
  channel: '',
  summary: '',
  content: '',
  sent_at: '',
  metadata: '{}',
};
