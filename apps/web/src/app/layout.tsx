import type { Metadata } from "next";
import { LocaleProvider } from "@/components/LocaleProvider";
import { SiteHeader } from "@/components/SiteHeader";
import "./globals.css";

export const metadata: Metadata = {
  title: "QuickPickr — Compare quick-commerce prices",
  description: "Compare Blinkit, Zepto, BigBasket, and Instamart prices in one search.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <LocaleProvider>
          <main className="mx-auto min-h-screen max-w-3xl px-4 py-6">
            <SiteHeader />
            {children}
          </main>
        </LocaleProvider>
      </body>
    </html>
  );
}
