/** Generated from packages/api-contract/openapi.yaml — keep in sync manually for MVP */

export type RowStatus = "available" | "unavailable" | "error";
export type MatchConfidence = "high" | "low";

export interface SearchRequest {
  query: string;
  pincode: string;
}

export interface SearchResultRow {
  retailer: string;
  retailerDisplayName: string;
  title: string;
  packSize: string;
  imageUrl: string;
  finalPriceInr: number | null;
  unitPriceLabel: string | null;
  matchConfidence: MatchConfidence;
  status: RowStatus;
  crawledAt: string | null;
  buyUrl: string | null;
  message: string | null;
}

export interface SearchMeta {
  cacheHit: boolean;
  latencyMs: number;
  vertexServingConfig?: string | null;
}

export interface SearchResponse {
  query: string;
  pincode: string;
  searchedAt: string;
  results: SearchResultRow[];
  meta: SearchMeta;
}

export interface HealthResponse {
  status: "ok" | "degraded" | "error";
  vertexConfigured: boolean;
  credentialsPathSet: boolean;
  servingConfig?: string | null;
  message?: string | null;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public body?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
