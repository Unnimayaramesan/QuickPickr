import type { Locale } from "@quickpickr/shared";
import { t } from "@quickpickr/shared";

export function TrustFooter({ locale }: { locale: Locale }) {
  return (
    <footer className="mt-8 border-t border-qp-border pt-4 text-sm text-qp-muted">
      <p>{t(locale, "trustFooter")}</p>
      <p className="mt-2 text-xs">{t(locale, "confirmCheckout")}</p>
    </footer>
  );
}
