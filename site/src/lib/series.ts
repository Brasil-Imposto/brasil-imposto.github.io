// Pure functions over the series of the entity files (phase B0). Each one is covered by tests in series.test.ts.

export interface Series {
  values: (number | null)[];
}

/** The last value the source published and its position, or null when the series has none. */
export function latest(values: readonly (number | null)[]): { index: number; value: number } | null {
  for (let i = values.length - 1; i >= 0; i--) {
    const v = values[i];
    if (v !== null && v !== undefined) return { index: i, value: v };
  }
  return null;
}

/** The sum of one year's months, only when every month of it is published; otherwise null (never a partial sum). */
export function yearTotal(months: readonly string[], values: readonly (number | null)[], year: number): number | null {
  let total = 0;
  let count = 0;
  for (let i = 0; i < months.length; i++) {
    if (!months[i]!.startsWith(`${year}-`)) continue;
    const v = values[i];
    if (v === null || v === undefined) return null;
    total += Math.round(v * 100);
    count++;
  }
  return count === 12 ? total / 100 : null;
}

/** A number written the Brazilian way, as the pages show it. */
export function formatBR(value: number, digits = 0): string {
  return value.toLocaleString('pt-BR', { minimumFractionDigits: digits, maximumFractionDigits: digits });
}
