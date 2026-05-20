export type AnalyticsEventName =
  | "search_completed"
  | "retailer_clickout"
  | "stale_row_shown"
  | "trust_feedback";

export interface AnalyticsPayload {
  sessionId: string;
  [key: string]: unknown;
}

type Sink = (event: AnalyticsEventName, payload: AnalyticsPayload) => void;

let sink: Sink = (event, payload) => {
  if (typeof console !== "undefined") {
    console.debug("[QuickPickr analytics]", event, payload);
  }
};

export function setAnalyticsSink(custom: Sink): void {
  sink = custom;
}

export function track(event: AnalyticsEventName, payload: AnalyticsPayload): void {
  sink(event, payload);
}
