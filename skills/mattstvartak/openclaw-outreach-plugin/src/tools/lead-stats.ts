import { Type } from '@sinclair/typebox';
import type { LeadDB } from '../db/connection.js';
import type { Lead, LeadStage } from '../types/index.js';
import { today, isOnOrBefore, daysBetween } from '../utils/dates.js';

export const definition = {
  name: 'lead_stats',
  label: 'Pipeline Stats',
  description: 'Pipeline summary: count by stage, total estimated value, won revenue, conversion rate, avg days to close, leads due for follow-up today.',
  parameters: Type.Object({}),
};

export async function execute(db: LeadDB, _config: any, _params: any) {
  const all = await db.queryLeads();
  const t = today();

  const byStage: Record<string, number> = {};
  let estimatedPipeline = 0;
  let wonRevenue = 0;
  let wonCount = 0;
  let lostCount = 0;
  const closeDays: number[] = [];
  let dueCount = 0;

  for (const lead of all) {
    byStage[lead.stage] = (byStage[lead.stage] ?? 0) + 1;

    if (lead.stage !== 'won' && lead.stage !== 'lost' && lead.stage !== 'dead') {
      estimatedPipeline += lead.estimatedValue ?? 0;
    }

    if (lead.stage === 'won') {
      wonCount++;
      wonRevenue += lead.actualValue ?? lead.estimatedValue ?? 0;
      if (lead.closedAt) {
        closeDays.push(daysBetween(lead.createdAt, lead.closedAt));
      }
    }

    if (lead.stage === 'lost') lostCount++;

    if (lead.nextActionDate && isOnOrBefore(lead.nextActionDate, t)) {
      dueCount++;
    }
  }

  const conversionRate = wonCount + lostCount > 0
    ? Math.round((wonCount / (wonCount + lostCount)) * 100)
    : 0;

  const avgDaysToClose = closeDays.length > 0
    ? Math.round(closeDays.reduce((a, b) => a + b, 0) / closeDays.length)
    : null;

  return jsonResult({
    totalLeads: all.length,
    byStage,
    estimatedPipeline,
    wonRevenue,
    conversionRate: `${conversionRate}%`,
    avgDaysToClose,
    dueForFollowUp: dueCount,
  });
}

function textResult(text: string) {
  return { content: [{ type: 'text' as const, text }] };
}

function jsonResult(data: any) {
  return textResult(JSON.stringify(data, null, 2));
}
