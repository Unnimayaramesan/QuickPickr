const RETAILERS = ["Blinkit", "Zepto", "BigBasket", "Instamart"];

export function SearchSkeleton() {
  return (
    <div aria-busy="true" aria-label="Loading results" className="animate-pulse space-y-3">
      {RETAILERS.map((name) => (
        <div key={name} className="flex gap-3 rounded-xl bg-qp-surface p-4 shadow-sm">
          <div className="h-10 w-10 rounded-full bg-qp-border" />
          <div className="flex-1 space-y-2">
            <div className="h-4 w-3/4 rounded bg-qp-border" />
            <div className="h-3 w-1/2 rounded bg-qp-border" />
          </div>
          <div className="h-8 w-20 rounded bg-qp-border" />
        </div>
      ))}
    </div>
  );
}
