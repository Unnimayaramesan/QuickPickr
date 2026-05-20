export const STORAGE_KEYS = {
  pincode: "quickpickr_pincode",
  sessionId: "quickpickr_session_id",
  history: "quickpickr_search_history",
  locale: "quickpickr_locale",
} as const;

export interface SearchHistoryEntry {
  query: string;
  pincode: string;
  searchedAt: string;
}

export const MAX_HISTORY = 20;

export function parseHistory(raw: string | null): SearchHistoryEntry[] {
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw) as SearchHistoryEntry[];
    return Array.isArray(parsed) ? parsed.slice(0, MAX_HISTORY) : [];
  } catch {
    return [];
  }
}

export function pushHistory(
  existing: SearchHistoryEntry[],
  entry: SearchHistoryEntry,
): SearchHistoryEntry[] {
  const filtered = existing.filter(
    (e) => !(e.query === entry.query && e.pincode === entry.pincode),
  );
  return [entry, ...filtered].slice(0, MAX_HISTORY);
}
