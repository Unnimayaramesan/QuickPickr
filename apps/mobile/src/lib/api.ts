import { QuickPickrClient } from "@quickpickr/api-client";
import { getOrCreateSessionIdAsync } from "@quickpickr/shared";
import { mobileStorage } from "./storage";

const baseUrl =
  process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8080";

let client: QuickPickrClient | null = null;

export async function getApiClient(): Promise<QuickPickrClient> {
  if (!client) {
    const sessionId = await getOrCreateSessionIdAsync(
      (k) => mobileStorage.getItem(k),
      (k, v) => mobileStorage.setItem(k, v),
    );
    client = new QuickPickrClient({ baseUrl, sessionId });
  }
  return client;
}
