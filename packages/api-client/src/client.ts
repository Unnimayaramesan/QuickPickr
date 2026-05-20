import type { HealthResponse, SearchRequest, SearchResponse } from "./types";
import { ApiError } from "./types";

export interface QuickPickrClientOptions {
  baseUrl: string;
  sessionId?: string;
  fetchImpl?: typeof fetch;
}

export class QuickPickrClient {
  private baseUrl: string;
  private sessionId: string;
  private fetchImpl: typeof fetch;

  constructor(options: QuickPickrClientOptions) {
    this.baseUrl = options.baseUrl.replace(/\/$/, "");
    this.sessionId = options.sessionId ?? "";
    // Native fetch loses its `this` binding when assigned to a property,
    // throwing "Illegal invocation" on call. Bind it to globalThis.
    this.fetchImpl = options.fetchImpl ?? fetch.bind(globalThis);
  }

  setSessionId(sessionId: string): void {
    this.sessionId = sessionId;
  }

  private headers(): HeadersInit {
    const h: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };
    if (this.sessionId) {
      h["X-Session-Id"] = this.sessionId;
    }
    return h;
  }

  private async parseError(res: Response): Promise<ApiError> {
    let body: unknown;
    try {
      body = await res.json();
    } catch {
      body = await res.text();
    }
    const detail =
      typeof body === "object" && body !== null && "detail" in body
        ? String((body as { detail: unknown }).detail)
        : res.statusText;
    const messages: Record<number, string> = {
      400: "Please check your product name and pincode.",
      429: "Too many searches. Please wait a moment and try again.",
      503: "Search is temporarily unavailable. Please try again.",
    };
    return new ApiError(messages[res.status] ?? detail, res.status, body);
  }

  async health(): Promise<HealthResponse> {
    const res = await this.fetchImpl(`${this.baseUrl}/health`, {
      headers: this.headers(),
    });
    if (!res.ok) throw await this.parseError(res);
    return res.json() as Promise<HealthResponse>;
  }

  async search(body: SearchRequest): Promise<SearchResponse> {
    const res = await this.fetchImpl(`${this.baseUrl}/v1/search`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify(body),
    });
    if (!res.ok) throw await this.parseError(res);
    return res.json() as Promise<SearchResponse>;
  }
}
