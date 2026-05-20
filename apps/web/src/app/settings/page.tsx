"use client";

import Link from "next/link";
import { STORAGE_KEYS, t, track } from "@quickpickr/shared";
import { webStorage } from "@/lib/storage";
import { useLocale } from "@/components/LocaleProvider";

export default function SettingsPage() {
  const { locale } = useLocale();

  const clearPincode = () => webStorage.removeItem(STORAGE_KEYS.pincode);
  const clearHistory = () => webStorage.removeItem(STORAGE_KEYS.history);

  const submitTrust = (rating: number) => {
    track("trust_feedback", {
      sessionId: webStorage.getItem(STORAGE_KEYS.sessionId) ?? "",
      rating,
    });
    alert("Thank you for your feedback.");
  };

  return (
    <div>
      <h1 className="mb-4 text-2xl font-bold">{t(locale, "settings")}</h1>
      <div className="space-y-4">
        <button
          type="button"
          onClick={clearPincode}
          className="min-h-[44px] w-full rounded-lg border border-qp-border bg-qp-surface px-4 py-3 text-left font-medium hover:bg-qp-bg"
        >
          {t(locale, "clearPincode")}
        </button>
        <button
          type="button"
          onClick={clearHistory}
          className="min-h-[44px] w-full rounded-lg border border-qp-border bg-qp-surface px-4 py-3 text-left font-medium hover:bg-qp-bg"
        >
          {t(locale, "clearHistory")}
        </button>
        <div className="rounded-lg border border-qp-border bg-qp-surface p-4">
          <p className="mb-2 text-sm font-semibold">Trust feedback (beta)</p>
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((n) => (
              <button
                key={n}
                type="button"
                onClick={() => submitTrust(n)}
                className="min-h-[44px] min-w-[44px] rounded border border-qp-border hover:bg-qp-bg"
                aria-label={`Rate ${n}`}
              >
                {n}
              </button>
            ))}
          </div>
        </div>
      </div>
      <Link href="/" className="mt-6 inline-block text-qp-primary hover:underline">
        ← Back
      </Link>
    </div>
  );
}
