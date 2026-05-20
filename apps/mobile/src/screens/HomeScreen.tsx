import { useCallback, useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  Linking,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import type { SearchResponse, SearchResultRow } from "@quickpickr/api-client";
import { ApiError } from "@quickpickr/api-client";
import { colors, touchTargetMin } from "@quickpickr/design-tokens";
import {
  applyAffiliateParams,
  formatFreshness,
  getOrCreateSessionIdAsync,
  isLowestRow,
  isStale,
  lowestPrice,
  parseHistory,
  pushHistory,
  sortResults,
  STORAGE_KEYS,
  t,
  track,
  type Locale,
} from "@quickpickr/shared";
import * as Location from "expo-location";
import { getApiClient } from "../lib/api";
import { affiliateConfig } from "../lib/affiliates";
import { mobileStorage } from "../lib/storage";

export function HomeScreen({
  locale,
  navigation,
}: {
  locale: Locale;
  navigation: { navigate: (s: string) => void };
}) {
  const [query, setQuery] = useState("");
  const [pincode, setPincode] = useState("");
  const [loading, setLoading] = useState(false);
  const [showSkeleton, setShowSkeleton] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<SearchResponse | null>(null);
  const sessionId = useRef("");

  useEffect(() => {
    (async () => {
      sessionId.current = await getOrCreateSessionIdAsync(
        (k) => mobileStorage.getItem(k),
        (k, v) => mobileStorage.setItem(k, v),
      );
      const saved = await mobileStorage.getItem(STORAGE_KEYS.pincode);
      if (saved) setPincode(saved);
    })();
  }, []);

  const runSearch = useCallback(async () => {
    setError(null);
    setData(null);
    setLoading(true);
    const tId = setTimeout(() => setShowSkeleton(true), 200);
    try {
      const client = await getApiClient();
      const res = await client.search({ query: query.trim(), pincode: pincode.trim() });
      setData(res);
      for (const row of res.results) {
        if (row.status === "available" && isStale(row.crawledAt)) {
          track("stale_row_shown", {
            sessionId: sessionId.current,
            retailer: row.retailer,
            query: res.query,
            pincode: res.pincode,
            searchedAt: res.searchedAt,
          });
        }
      }
      await mobileStorage.setItem(STORAGE_KEYS.pincode, pincode.trim());
      const raw = await mobileStorage.getItem(STORAGE_KEYS.history);
      const next = pushHistory(parseHistory(raw), {
        query: res.query,
        pincode: res.pincode,
        searchedAt: res.searchedAt,
      });
      await mobileStorage.setItem(STORAGE_KEYS.history, JSON.stringify(next));
      track("search_completed", {
        sessionId: sessionId.current,
        query: res.query,
        pincode: res.pincode,
        latencyMs: res.meta.latencyMs,
        cacheHit: res.meta.cacheHit,
      });
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Search failed");
    } finally {
      clearTimeout(tId);
      setShowSkeleton(false);
      setLoading(false);
    }
  }, [query, pincode]);

  const onBuy = async (row: SearchResultRow) => {
    if (!row.buyUrl) return;
    const url = applyAffiliateParams(row.buyUrl, row.retailer, affiliateConfig);
    track("retailer_clickout", {
      sessionId: sessionId.current,
      retailer: row.retailer,
      finalPriceInr: row.finalPriceInr,
    });
    await Linking.openURL(url);
  };

  const onLocation = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== "granted") {
      setError(t(locale, "locationError"));
      return;
    }
    const loc = await Location.getCurrentPositionAsync({});
    const rev = await Location.reverseGeocodeAsync(loc.coords);
    const pc = rev[0]?.postalCode?.replace(/\D/g, "").slice(0, 6);
    if (pc && /^[1-9][0-9]{5}$/.test(pc)) setPincode(pc);
    else setError(t(locale, "locationError"));
  };

  const sorted = data ? sortResults(data.results) : [];
  const low = data ? lowestPrice(sorted) : null;

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>{t(locale, "appName")}</Text>
      <Text style={styles.tagline}>{t(locale, "tagline")}</Text>

      <Text style={styles.label}>{t(locale, "productLabel")}</Text>
      <TextInput
        value={query}
        onChangeText={setQuery}
        placeholder={t(locale, "productPlaceholder")}
        style={styles.input}
        accessibilityLabel={t(locale, "productLabel")}
      />
      <Text style={styles.label}>{t(locale, "pincodeLabel")}</Text>
      <TextInput
        value={pincode}
        onChangeText={(v) => setPincode(v.replace(/\D/g, "").slice(0, 6))}
        placeholder={t(locale, "pincodePlaceholder")}
        keyboardType="number-pad"
        style={styles.input}
        maxLength={6}
      />
      <Pressable onPress={onLocation} style={styles.linkBtn}>
        <Text style={styles.linkText}>{t(locale, "useLocation")}</Text>
      </Pressable>
      <Pressable
        onPress={runSearch}
        disabled={loading}
        style={[styles.primaryBtn, loading && styles.disabled]}
        accessibilityRole="button"
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.primaryText}>{t(locale, "search")}</Text>
        )}
      </Pressable>

      <View style={styles.navRow}>
        <Pressable onPress={() => navigation.navigate("History")}>
          <Text style={styles.linkText}>{t(locale, "history")}</Text>
        </Pressable>
        <Pressable onPress={() => navigation.navigate("Settings")}>
          <Text style={styles.linkText}>{t(locale, "settings")}</Text>
        </Pressable>
        <Pressable onPress={() => navigation.navigate("Privacy")}>
          <Text style={styles.linkText}>{t(locale, "privacy")}</Text>
        </Pressable>
      </View>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      {showSkeleton && loading ? (
        <View style={styles.skeletonBlock}>
          {[1, 2, 3, 4].map((i) => (
            <View key={i} style={styles.skeletonRow} />
          ))}
        </View>
      ) : null}

      {data && !loading
        ? sorted.map((row) => {
            const stale = isStale(row.crawledAt);
            const lowest = isLowestRow(row, low);
            return (
              <View key={row.retailer} style={styles.card}>
                <View style={styles.rowHeader}>
                  <Text style={styles.retailer}>{row.retailerDisplayName}</Text>
                  {lowest ? (
                    <Text style={styles.lowest}>{t(locale, "lowestPrice")}</Text>
                  ) : null}
                </View>
                {row.status === "available" ? (
                  <>
                    <Text style={styles.productTitle}>{row.title}</Text>
                    {row.packSize ? <Text style={styles.muted}>{row.packSize}</Text> : null}
                    {row.matchConfidence === "low" ? (
                      <Text style={styles.warn}>{t(locale, "closestMatch")}</Text>
                    ) : null}
                    <Text style={styles.muted}>{formatFreshness(row.crawledAt, locale)}</Text>
                    {stale ? <Text style={styles.warn}>{t(locale, "stalePrice")}</Text> : null}
                    {row.finalPriceInr != null ? (
                      <Text style={styles.price}>
                        ₹{row.finalPriceInr.toLocaleString("en-IN")}
                      </Text>
                    ) : null}
                    {row.buyUrl ? (
                      <Pressable
                        onPress={() => onBuy(row)}
                        style={styles.primaryBtn}
                        accessibilityRole="button"
                      >
                        <Text style={styles.primaryText}>
                          {t(locale, "buyOn")} {row.retailerDisplayName}
                        </Text>
                      </Pressable>
                    ) : null}
                  </>
                ) : (
                  <Text style={styles.muted}>
                    {row.status === "unavailable"
                      ? t(locale, "notAvailable")
                      : t(locale, "temporarilyUnavailable")}
                  </Text>
                )}
              </View>
            );
          })
        : null}

      <Text style={styles.footer}>{t(locale, "trustFooter")}</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, paddingBottom: 40, backgroundColor: colors.background },
  title: { fontSize: 24, fontWeight: "700", color: colors.primary },
  tagline: { color: colors.textMuted, marginBottom: 16 },
  label: { fontWeight: "600", marginBottom: 4 },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    backgroundColor: colors.surface,
    minHeight: touchTargetMin,
  },
  primaryBtn: {
    backgroundColor: colors.primary,
    borderRadius: 8,
    padding: 14,
    alignItems: "center",
    minHeight: touchTargetMin,
    marginVertical: 8,
  },
  primaryText: { color: "#fff", fontWeight: "600" },
  disabled: { opacity: 0.6 },
  linkBtn: { marginBottom: 8 },
  linkText: { color: colors.primary, fontWeight: "500" },
  navRow: { flexDirection: "row", gap: 16, marginVertical: 12 },
  error: { color: colors.error, marginVertical: 8 },
  skeletonBlock: { marginTop: 16, gap: 8 },
  skeletonRow: { height: 80, backgroundColor: colors.border, borderRadius: 12 },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    marginTop: 12,
    borderWidth: 1,
    borderColor: colors.border,
  },
  rowHeader: { flexDirection: "row", alignItems: "center", gap: 8 },
  retailer: { fontWeight: "700", fontSize: 16 },
  lowest: { color: colors.primary, fontWeight: "700", fontSize: 12 },
  productTitle: { fontWeight: "600", marginTop: 8 },
  muted: { color: colors.textMuted, marginTop: 4 },
  warn: { color: colors.warning, marginTop: 4, fontWeight: "500" },
  price: { fontSize: 20, fontWeight: "700", marginVertical: 8 },
  footer: { marginTop: 24, fontSize: 12, color: colors.textMuted },
});
