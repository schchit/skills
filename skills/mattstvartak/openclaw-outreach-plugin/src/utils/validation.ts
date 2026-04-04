import type { LeadStage } from '../types/index.js';

const VALID_TRANSITIONS: Record<LeadStage, LeadStage[]> = {
  identified: ['researched', 'dead'],
  researched: ['contacted', 'dead'],
  contacted: ['replied', 'dead', 'lost'],
  replied: ['negotiating', 'won', 'lost', 'dead'],
  negotiating: ['won', 'lost', 'dead'],
  won: [],
  lost: ['contacted'],
  dead: [],
};

export function validateTransition(from: LeadStage, to: LeadStage): string | null {
  if (from === to) return `Lead is already in stage "${from}".`;
  const allowed = VALID_TRANSITIONS[from];
  if (!allowed || allowed.length === 0) {
    return `Stage "${from}" is terminal. No transitions allowed.`;
  }
  if (!allowed.includes(to)) {
    return `Cannot move from "${from}" to "${to}". Valid transitions: ${allowed.join(', ')}.`;
  }
  return null;
}

export function isTerminalStage(stage: LeadStage): boolean {
  return stage === 'won' || stage === 'dead';
}

export function isClosedStage(stage: LeadStage): boolean {
  return stage === 'won' || stage === 'lost' || stage === 'dead';
}

export function esc(val: string): string {
  return val.replace(/'/g, "''");
}
