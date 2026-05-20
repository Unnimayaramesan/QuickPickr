"use client";

import { useEffect } from "react";
import type { SearchResultRow } from "@quickpickr/api-client";
import type { AffiliateMap, Locale } from "@quickpickr/shared";
import {
  applyAffiliateParams,
  formatFreshness,
  isLowestRow,
  isStale,
  lowestPrice,
  sortResults,
  t,
  track,
} from "@quickpickr/shared";
import { RetailerLogo } from "./RetailerLogo";

export interface ResultsTableProps {
  rows: SearchResultRow[];
  locale: Locale;
  sessionId: string;
  affiliates: AffiliateMap;
  query: string;
  pincode: string;
  searchedAt: string;
}

export function ResultsTable({
  rows,
  locale,
  sessionId,
  affiliates,
  query,
  pincode,
  searchedAt,
}: ResultsTableProps) {
  const sorted = sortResults(rows);
  const lowest = lowestPrice(sorted);

  useEffect(() => {
    const ordered = sortResults(rows);
    for (const row of ordered) {
      if (row.status === "available" && isStale(row.crawledAt)) {
        track("stale_row_shown", {
          sessionId,
          retailer: row.retailer,
          query,
          pincode,
          searchedAt,
        });
      }
    }
  }, [rows, searchedAt, sessionId, query, pincode]);

  const handleBuy = (row: SearchResultRow) => {
    if (!row.buyUrl) return;
    const url = applyAffiliateParams(row.buyUrl, row.retailer, affiliates);
    track("retailer_clickout", {
      sessionId,
      retailer: row.retailer,
      rankPosition: sorted.indexOf(row) + 1,
      finalPriceInr: row.finalPriceInr,
      query,
      pincode,
    });
    window.open(url, "_blank", "noopener,noreferrer");
  };

  return (
    <div
      className="overflow-hidden rounded-xl bg-qp-surface shadow-sm"
      aria-live="polite"
      aria-label="Price comparison results"
    >
      <table className="w-full text-left text-sm">
        <thead className="sr-only">
          <tr>
            <th scope="col">Retailer</th>
            <th scope="col">Product</th>
            <th scope="col">Price</th>
            <th scope="col">Action</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((row) => {
            const stale = isStale(row.crawledAt);
            const showLowest = isLowestRow(row, lowest);
            return (
              <tr key={row.retailer} className="border-b border-qp-border last:border-0">
                <td className="p-4 align-top">
                  <div className="flex items-center gap-2">
                    <RetailerLogo retailer={row.retailer} name={row.retailerDisplayName} />
                    <div>
                      <span className="font-semibold">{row.retailerDisplayName}</span>
                      {showLowest && (
                        <span className="ml-2 text-xs font-bold text-qp-primary">
                          {t(locale, "lowestPrice")}
                        </span>
                      )}
                    </div>
                  </div>
                </td>
                <td className="p-4 align-top">
                  {row.status === "available" ? (
                    <>
                      <div className="flex gap-3">
                        {row.imageUrl ? (
                          <img
                            src={row.imageUrl}
                            alt=""
                            className="h-14 w-14 rounded object-cover"
                          />
                        ) : null}
                        <div>
                          <p className="font-medium">{row.title || "—"}</p>
                          {row.packSize ? (
                            <p className="text-qp-muted">{row.packSize}</p>
                          ) : null}
                          {row.matchConfidence === "low" && (
                            <p className="mt-1 text-xs font-medium text-qp-warning">
                              {t(locale, "closestMatch")}
                            </p>
                          )}
                          <p className="mt-1 text-xs text-qp-muted">
                            {formatFreshness(row.crawledAt, locale)}
                          </p>
                          {stale && (
                            <p className="text-xs font-medium text-qp-warning">
                              {t(locale, "stalePrice")}
                            </p>
                          )}
                        </div>
                      </div>
                    </>
                  ) : (
                    <p className="text-qp-muted">
                      {row.status === "unavailable"
                        ? t(locale, "notAvailable")
                        : row.message ?? t(locale, "temporarilyUnavailable")}
                    </p>
                  )}
                </td>
                <td className="p-4 align-top">
                  {row.finalPriceInr != null ? (
                    <span className="text-lg font-bold">
                      ₹{row.finalPriceInr.toLocaleString("en-IN")}
                    </span>
                  ) : (
                    <span className="text-qp-muted">—</span>
                  )}
                  {row.unitPriceLabel ? (
                    <p className="text-xs text-qp-muted">{row.unitPriceLabel}</p>
                  ) : null}
                </td>
                <td className="p-4 align-top">
                  {row.status === "available" && row.buyUrl ? (
                    <button
                      type="button"
                      onClick={() => handleBuy(row)}
                      className="min-h-[44px] whitespace-nowrap rounded-lg bg-qp-primary px-3 py-2 text-sm font-semibold text-white hover:bg-blue-800"
                    >
                      {t(locale, "buyOn")} {row.retailerDisplayName}
                    </button>
                  ) : null}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
