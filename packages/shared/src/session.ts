import { STORAGE_KEYS } from "./storage";

export function createSessionId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `qp-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}

export function getOrCreateSessionId(
  getItem: (key: string) => string | null,
  setItem: (key: string, value: string) => void,
): string {
  let id = getItem(STORAGE_KEYS.sessionId);
  if (!id) {
    id = createSessionId();
    setItem(STORAGE_KEYS.sessionId, id);
  }
  return id;
}

export async function getOrCreateSessionIdAsync(
  getItem: (key: string) => Promise<string | null>,
  setItem: (key: string, value: string) => Promise<void>,
): Promise<string> {
  let id = await getItem(STORAGE_KEYS.sessionId);
  if (!id) {
    id = createSessionId();
    await setItem(STORAGE_KEYS.sessionId, id);
  }
  return id;
}
