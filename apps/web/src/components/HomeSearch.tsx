"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { SearchResponse } from "@quickpickr/api-client";
import { ApiError } from "@quickpickr/api-client";
import {
  getOrCreateSessionId,
  parseHistory,
  pushHistory,
  STORAGE_KEYS,
  track,
  t,
} from "@quickpickr/shared";
import { getApiClient } from "@/lib/api";
import { affiliateConfig } from "@/lib/config";
import { pincodeFromCoords } from "@/lib/geocode";
import { webStorage } from "@/lib/storage";
import { useLocale } from "./LocaleProvider";
import { ResultsTable } from "./ResultsTable";
import { SearchForm } from "./SearchForm";
import { SearchSkeleton } from "./SearchSkeleton";
import { TrustFooter } from "./TrustFooter";

export function HomeSearch() {
  const { locale } = useLocale();
  const [query, setQuery] = useState("");
  const [pincode, setPincode] = useState("");
  const [loading, setLoading] = useState(false);
  const [showSkeleton, setShowSkeleton] = useState(false);
  const [locationLoading, setLocationLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<SearchResponse | null>(null);
  const sessionIdRef = useRef("");
  const skeletonTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    sessionIdRef.current = getOrCreateSessionId(
      (k) => webStorage.getItem(k),
      (k, v) => webStorage.setItem(k, v),
    );
    const saved = webStorage.getItem(STORAGE_KEYS.pincode);
    if (saved) setPincode(saved);
  }, []);

  const runSearch = useCallback(async () => {
    setError(null);
    setData(null);
    setLoading(true);
    setShowSkeleton(false);
    skeletonTimer.current = setTimeout(() => setShowSkeleton(true), 200);

    try {
      const client = getApiClient();
      const res = await client.search({ query: query.trim(), pincode: pincode.trim() });
      setData(res);
      webStorage.setItem(STORAGE_KEYS.pincode, pincode.trim());
      const hist = parseHistory(webStorage.getItem(STORAGE_KEYS.history));
      const next = pushHistory(hist, {
        query: res.query,
        pincode: res.pincode,
        searchedAt: res.searchedAt,
      });
      webStorage.setItem(STORAGE_KEYS.history, JSON.stringify(next));
      track("search_completed", {
        sessionId: sessionIdRef.current,
        query: res.query,
        pincode: res.pincode,
        retailersReturned: res.results.map((r) => r.retailer),
        pricesInr: res.results.map((r) => r.finalPriceInr),
        latencyMs: res.meta.latencyMs,
        cacheHit: res.meta.cacheHit,
      });
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Search failed");
    } finally {
      if (skeletonTimer.current) clearTimeout(skeletonTimer.current);
      setShowSkeleton(false);
      setLoading(false);
    }
  }, [query, pincode]);

  const onUseLocation = async () => {
    if (!navigator.geolocation) {
      setError(t(locale, "locationError"));
      return;
    }
    setLocationLoading(true);
    setError(null);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const pc = await pincodeFromCoords(pos.coords.latitude, pos.coords.longitude);
          if (pc) setPincode(pc);
          else setError(t(locale, "locationError"));
        } catch {
          setError(t(locale, "locationError"));
        } finally {
          setLocationLoading(false);
        }
      },
      () => {
        setError(t(locale, "locationError"));
        setLocationLoading(false);
      },
    );
  };

  const hasAvailable = data?.results.some((r) => r.status === "available");
  const showResultsTable = Boolean(data?.results.length);

  return (
    <>
      <SearchForm
        locale={locale}
        query={query}
        pincode={pincode}
        loading={loading}
        onQueryChange={setQuery}
        onPincodeChange={setPincode}
        onSubmit={runSearch}
        onUseLocation={onUseLocation}
        locationLoading={locationLoading}
      />

      {error && (
        <p className="mt-4 rounded-lg bg-red-50 p-3 text-qp-error" role="alert">
          {error}
        </p>
      )}

      {showSkeleton && loading && <div className="mt-6"><SearchSkeleton /></div>}

      {data && !loading && (
        <div className="mt-6">
          {!hasAvailable && (
            <p className="mb-4 rounded-lg bg-qp-surface p-4 text-qp-muted">{t(locale, "noResults")}</p>
          )}
          {showResultsTable && (
            <ResultsTable
              rows={data.results}
              locale={locale}
              sessionId={sessionIdRef.current}
              affiliates={affiliateConfig}
              query={data.query}
              pincode={data.pincode}
              searchedAt={data.searchedAt}
            />
          )}
          <p className="mt-2 text-xs text-qp-muted">
            {data.meta.latencyMs}ms{data.meta.cacheHit ? " · cached" : ""}
          </p>
        </div>
      )}

      <TrustFooter locale={locale} />
    </>
  );
}
