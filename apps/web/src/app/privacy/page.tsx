import Link from "next/link";

export default function PrivacyPage() {
  return (
    <article className="prose prose-sm max-w-none">
      <h1 className="text-2xl font-bold">Privacy notice (DPDP)</h1>
      <p className="text-qp-muted">Last updated: May 2026</p>

      <h2 className="mt-6 text-lg font-semibold">What we collect</h2>
      <ul className="list-disc pl-5 text-qp-muted">
        <li>Product search queries you enter</li>
        <li>Pincode (stored on your device only in v1)</li>
        <li>An anonymous session identifier for analytics</li>
      </ul>

      <h2 className="mt-6 text-lg font-semibold">What we do not collect (v1)</h2>
      <ul className="list-disc pl-5 text-qp-muted">
        <li>No account or login</li>
        <li>No payment information</li>
        <li>No server-side storage of your search history tied to identity</li>
      </ul>

      <h2 className="mt-6 text-lg font-semibold">How we use data</h2>
      <p className="text-qp-muted">
        Search queries are sent to our API to retrieve indexed public prices from retailer
        websites. Analytics events help us improve reliability and performance.
      </p>

      <h2 className="mt-6 text-lg font-semibold">Your choices</h2>
      <p className="text-qp-muted">
        Clear saved pincode and search history anytime in Settings. Purchases complete on
        retailer apps — their privacy policies apply at checkout.
      </p>

      <Link href="/" className="mt-8 inline-block text-qp-primary hover:underline">
        ← Back to search
      </Link>
    </article>
  );
}
