import { Type } from '@sinclair/typebox';
import type { LeadDB } from '../db/connection.js';
import type { Lead } from '../types/index.js';
import { today, isOnOrBefore, daysBetween } from '../utils/dates.js';

export const definition = {
  name: 'lead_due',
  label: 'Due Follow-ups',
  description: 'Return all leads where nextActionDate is today or past due. Sorted by most overdue first. Check this at session start.',
  parameters: Type.Object({}),
};

export async function execute(db: LeadDB, config: any, _params: any) {
  const all = await db.queryLeads();
  const t = today();

  const due = all
    .filter(l => l.nextActionDate && isOnOrBefore(l.nextActionDate, t))
    .sort((a, b) => (a.nextActionDate ?? '').localeCompare(b.nextActionDate ?? ''));

  const overdueThreshold = config.overdueAlertDays ?? 3;

  return jsonResult({
    count: due.length,
    leads: due.map(l => ({
      id: l.id,
      name: l.name,
      company: l.company,
      stage: l.stage,
      product: l.product,
      nextAction: l.nextAction,
      nextActionDate: l.nextActionDate,
      daysOverdue: daysBetween(l.nextActionDate!, t),
      overdue: daysBetween(l.nextActionDate!, t) >= overdueThreshold,
    })),
  });
}

function textResult(text: string) {
  return { content: [{ type: 'text' as const, text }] };
}

function jsonResult(data: any) {
  return textResult(JSON.stringify(data, null, 2));
}
