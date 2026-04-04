export function now(): string {
  return new Date().toISOString();
}

export function today(): string {
  return new Date().toISOString().split('T')[0];
}

export function daysBetween(a: string, b: string): number {
  const msPerDay = 86_400_000;
  const dateA = new Date(a).getTime();
  const dateB = new Date(b).getTime();
  return Math.round(Math.abs(dateB - dateA) / msPerDay);
}

export function isOnOrBefore(date: string, reference: string): boolean {
  return date.localeCompare(reference) <= 0;
}
