import { QuickPickrClient } from "@quickpickr/api-client";
import { getOrCreateSessionId } from "@quickpickr/shared";
import { webStorage } from "./storage";

const baseUrl =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8080";

let client: QuickPickrClient | null = null;

export function getApiClient(): QuickPickrClient {
  if (!client) {
    const sessionId = getOrCreateSessionId(
      (k) => webStorage.getItem(k),
      (k, v) => webStorage.setItem(k, v),
    );
    client = new QuickPickrClient({ baseUrl, sessionId });
  }
  return client;
}
