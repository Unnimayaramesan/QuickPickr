import type { SearchResultRow } from "@quickpickr/api-client";

const RETAILER_ORDER = ["blinkit", "zepto", "bigbasket", "instamart"] as const;

/** Sort ascending by price; unavailable/error rows last. Shared by web + mobile. */
export function sortResults(rows: SearchResultRow[]): SearchResultRow[] {
  return [...rows].sort((a, b) => {
    const aPrice = a.status === "available" && a.finalPriceInr != null ? a.finalPriceInr : Infinity;
    const bPrice = b.status === "available" && b.finalPriceInr != null ? b.finalPriceInr : Infinity;
    if (aPrice !== bPrice) return aPrice - bPrice;
    return RETAILER_ORDER.indexOf(a.retailer as (typeof RETAILER_ORDER)[number]) -
      RETAILER_ORDER.indexOf(b.retailer as (typeof RETAILER_ORDER)[number]);
  });
}

export function lowestPrice(rows: SearchResultRow[]): number | null {
  const available = rows.filter((r) => r.status === "available" && r.finalPriceInr != null);
  if (!available.length) return null;
  return Math.min(...available.map((r) => r.finalPriceInr as number));
}

export function isLowestRow(row: SearchResultRow, lowest: number | null): boolean {
  return (
    lowest !== null &&
    row.status === "available" &&
    row.finalPriceInr === lowest
  );
}
