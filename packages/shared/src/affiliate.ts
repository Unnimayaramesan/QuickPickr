export interface AffiliateConfig {
  enabled: boolean;
  params: Record<string, string>;
}

export type AffiliateMap = Record<string, AffiliateConfig>;

export function applyAffiliateParams(
  buyUrl: string,
  retailer: string,
  affiliates: AffiliateMap,
): string {
  const cfg = affiliates[retailer];
  if (!cfg?.enabled || !Object.keys(cfg.params).length) return buyUrl;
  try {
    const url = new URL(buyUrl);
    for (const [k, v] of Object.entries(cfg.params)) {
      url.searchParams.set(k, v);
    }
    return url.toString();
  } catch {
    return buyUrl;
  }
}
