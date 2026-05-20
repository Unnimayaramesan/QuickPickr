"use client";

import type { Locale } from "@quickpickr/shared";
import { t, validatePincode, validateQuery } from "@quickpickr/shared";

export interface SearchFormProps {
  locale: Locale;
  query: string;
  pincode: string;
  loading: boolean;
  onQueryChange: (v: string) => void;
  onPincodeChange: (v: string) => void;
  onSubmit: () => void;
  onUseLocation: () => void;
  locationLoading?: boolean;
}

export function SearchForm({
  locale,
  query,
  pincode,
  loading,
  onQueryChange,
  onPincodeChange,
  onSubmit,
  onUseLocation,
  locationLoading,
}: SearchFormProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateQuery(query) || !validatePincode(pincode)) return;
    onSubmit();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <label className="block">
        <span className="mb-1 block text-sm font-semibold">{t(locale, "productLabel")}</span>
        <input
          type="text"
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          placeholder={t(locale, "productPlaceholder")}
          minLength={2}
          maxLength={120}
          required
          className="w-full rounded-lg border border-qp-border bg-qp-surface px-3 py-3 text-base"
          autoComplete="off"
        />
      </label>
      <label className="block">
        <span className="mb-1 block text-sm font-semibold">{t(locale, "pincodeLabel")}</span>
        <input
          type="text"
          inputMode="numeric"
          pattern="[1-9][0-9]{5}"
          value={pincode}
          onChange={(e) => onPincodeChange(e.target.value.replace(/\D/g, "").slice(0, 6))}
          placeholder={t(locale, "pincodePlaceholder")}
          required
          className="w-full rounded-lg border border-qp-border bg-qp-surface px-3 py-3 text-base"
        />
      </label>
      <button
        type="button"
        onClick={onUseLocation}
        disabled={locationLoading || loading}
        className="text-sm font-medium text-qp-primary underline-offset-2 hover:underline disabled:opacity-50"
      >
        {locationLoading ? "…" : t(locale, "useLocation")}
      </button>
      <button
        type="submit"
        disabled={loading}
        className="min-h-[44px] w-full rounded-lg bg-qp-primary px-4 py-3 font-semibold text-white hover:bg-blue-800 disabled:opacity-60"
      >
        {loading ? t(locale, "searching") : t(locale, "search")}
      </button>
    </form>
  );
}
