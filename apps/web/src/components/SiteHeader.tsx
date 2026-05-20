"use client";

import Link from "next/link";
import { t } from "@quickpickr/shared";
import { useLocale } from "./LocaleProvider";

export function SiteHeader() {
  const { locale, setLocale } = useLocale();

  return (
    <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
      <div>
        <Link href="/" className="text-xl font-bold text-qp-primary">
          {t(locale, "appName")}
        </Link>
        <p className="text-sm text-qp-muted">{t(locale, "tagline")}</p>
      </div>
      <nav className="flex flex-wrap items-center gap-3 text-sm font-medium">
        <Link href="/history" className="text-qp-primary hover:underline">
          {t(locale, "history")}
        </Link>
        <Link href="/settings" className="text-qp-primary hover:underline">
          {t(locale, "settings")}
        </Link>
        <Link href="/privacy" className="text-qp-primary hover:underline">
          {t(locale, "privacy")}
        </Link>
        <label className="flex items-center gap-1">
          <span className="sr-only">{t(locale, "language")}</span>
          <select
            value={locale}
            onChange={(e) => setLocale(e.target.value as "en" | "hi")}
            className="rounded border border-qp-border bg-qp-surface px-2 py-1"
          >
            <option value="en">{t(locale, "english")}</option>
            <option value="hi">{t(locale, "hindi")}</option>
          </select>
        </label>
      </nav>
    </header>
  );
}
