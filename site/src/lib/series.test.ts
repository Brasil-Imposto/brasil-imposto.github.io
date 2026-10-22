import { describe, expect, it } from 'vitest';
import { formatBR, latest, yearTotal } from './series';

describe('latest', () => {
  it('skips the months not published yet', () => {
    expect(latest([1, 2, null, null])).toEqual({ index: 1, value: 2 });
  });
  it('is null when nothing is published', () => {
    expect(latest([null, null])).toBeNull();
  });
});

describe('yearTotal', () => {
  const months = Array.from({ length: 13 }, (_, i) => (i < 12 ? `2024-${String(i + 1).padStart(2, '0')}` : '2025-01'));
  it('adds the twelve months to the cent', () => {
    expect(yearTotal(months, [...Array(12).fill(0.1), 5], 2024)).toBe(1.2);
  });
  it('closes to the cent where floating point would not (0,29 x 12 = 3,48)', () => {
    expect(yearTotal(months, [...Array(12).fill(0.29), 5], 2024)).toBe(3.48);
  });
  it('gives no partial sum when a month is missing', () => {
    expect(yearTotal(months, [...Array(11).fill(1), null, 5], 2024)).toBeNull();
  });
  it('gives no sum for a year with fewer than twelve months', () => {
    expect(yearTotal(months, Array(13).fill(1), 2025)).toBeNull();
  });
});

describe('formatBR', () => {
  it('writes numbers as Brazilian pages do', () => {
    expect(formatBR(8312759)).toBe('8.312.759');
    expect(formatBR(1234.5, 2)).toBe('1.234,50');
  });
});
