const COLORS: Record<string, string> = {
  blinkit: "bg-yellow-400",
  zepto: "bg-purple-600",
  bigbasket: "bg-green-600",
  instamart: "bg-orange-500",
};

export function RetailerLogo({ retailer, name }: { retailer: string; name: string }) {
  const bg = COLORS[retailer] ?? "bg-gray-400";
  return (
    <div
      className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white ${bg}`}
      aria-hidden
    >
      {name.slice(0, 2).toUpperCase()}
    </div>
  );
}
