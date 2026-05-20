import { useEffect, useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { colors } from "@quickpickr/design-tokens";
import { parseHistory, STORAGE_KEYS, t, type Locale, type SearchHistoryEntry } from "@quickpickr/shared";
import { mobileStorage } from "../lib/storage";

export function HistoryScreen({
  locale,
  onRerun,
}: {
  locale: Locale;
  onRerun: (e: SearchHistoryEntry) => void;
}) {
  const [entries, setEntries] = useState<SearchHistoryEntry[]>([]);

  useEffect(() => {
    mobileStorage.getItem(STORAGE_KEYS.history).then((raw) => {
      setEntries(parseHistory(raw));
    });
  }, []);

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>{t(locale, "history")}</Text>
      {entries.length === 0 ? (
        <Text style={styles.muted}>No recent searches.</Text>
      ) : (
        entries.map((e) => (
          <Pressable key={`${e.query}-${e.searchedAt}`} style={styles.item} onPress={() => onRerun(e)}>
            <Text style={styles.query}>{e.query}</Text>
            <Text style={styles.muted}>{e.pincode}</Text>
          </Pressable>
        ))
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  title: { fontSize: 22, fontWeight: "700", marginBottom: 16 },
  muted: { color: colors.textMuted },
  item: {
    padding: 16,
    backgroundColor: colors.surface,
    borderRadius: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: colors.border,
  },
  query: { fontWeight: "600" },
});
