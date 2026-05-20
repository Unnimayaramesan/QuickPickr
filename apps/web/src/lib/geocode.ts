/** Reverse geocode lat/lon to Indian pincode via OpenStreetMap Nominatim (dev/P1; no API key). */
export async function pincodeFromCoords(lat: number, lon: number): Promise<string | null> {
  const url = new URL("https://nominatim.openstreetmap.org/reverse");
  url.searchParams.set("lat", String(lat));
  url.searchParams.set("lon", String(lon));
  url.searchParams.set("format", "json");
  url.searchParams.set("addressdetails", "1");

  const fetchBound = globalThis.fetch.bind(globalThis);
  const res = await fetchBound(url.toString(), {
    headers: { "User-Agent": "QuickPickr/1.0 (price comparison app; contact: dev@quickpickr.local)" },
  });
  if (!res.ok) return null;
  const data = (await res.json()) as { address?: { postcode?: string } };
  const pc = data.address?.postcode?.replace(/\D/g, "").slice(0, 6);
  if (pc && /^[1-9][0-9]{5}$/.test(pc)) return pc;
  return null;
}
