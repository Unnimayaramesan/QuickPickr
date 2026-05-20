const FRESHNESS_MINUTES = 5;

export function ageMinutesFromIso(crawledAt: string | null | undefined): number | null {
  if (!crawledAt) return null;
  const t = Date.parse(crawledAt);
  if (Number.isNaN(t)) return null;
  return Math.floor((Date.now() - t) / 60_000);
}

export function formatFreshness(crawledAt: string | null | undefined, locale: string): string {
  const age = ageMinutesFromIso(crawledAt);
  if (age === null) return locale === "hi" ? "अपडेट समय अज्ञात" : "Update time unknown";
  if (age <= 0) return locale === "hi" ? "अभी अपडेट किया गया" : "Updated just now";
  if (age === 1) return locale === "hi" ? "1 मिनट पहले अपडेट" : "Updated 1 min ago";
  return locale === "hi" ? `${age} मिनट पहले अपडेट` : `Updated ${age} min ago`;
}

export function isStale(crawledAt: string | null | undefined): boolean {
  const age = ageMinutesFromIso(crawledAt);
  return age !== null && age > FRESHNESS_MINUTES;
}
