"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { parseHistory, STORAGE_KEYS, type SearchHistoryEntry, t } from "@quickpickr/shared";
import { webStorage } from "@/lib/storage";
import { useLocale } from "@/components/LocaleProvider";

export default function HistoryPage() {
  const { locale } = useLocale();
  const router = useRouter();
  const [entries, setEntries] = useState<SearchHistoryEntry[]>([]);

  useEffect(() => {
    setEntries(parseHistory(webStorage.getItem(STORAGE_KEYS.history)));
  }, []);

  const rerun = (e: SearchHistoryEntry) => {
    const params = new URLSearchParams({ q: e.query, pincode: e.pincode });
    router.push(`/?${params.toString()}`);
  };

  return (
    <div>
      <h1 className="mb-4 text-2xl font-bold">{t(locale, "history")}</h1>
      {entries.length === 0 ? (
        <p className="text-qp-muted">No recent searches.</p>
      ) : (
        <ul className="space-y-2">
          {entries.map((e) => (
            <li key={`${e.query}-${e.pincode}-${e.searchedAt}`}>
              <button
                type="button"
                onClick={() => rerun(e)}
                className="w-full rounded-lg border border-qp-border bg-qp-surface px-4 py-3 text-left hover:bg-qp-bg"
              >
                <span className="font-medium">{e.query}</span>
                <span className="ml-2 text-qp-muted">{e.pincode}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
      <Link href="/" className="mt-6 inline-block text-qp-primary hover:underline">
        ← Back
      </Link>
    </div>
  );
}
