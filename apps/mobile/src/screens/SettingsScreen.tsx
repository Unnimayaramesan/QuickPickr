import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { colors, touchTargetMin } from "@quickpickr/design-tokens";
import { STORAGE_KEYS, t, track, type Locale } from "@quickpickr/shared";
import { mobileStorage } from "../lib/storage";

export function SettingsScreen({ locale }: { locale: Locale }) {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>{t(locale, "settings")}</Text>
      <Pressable
        style={styles.btn}
        onPress={() => mobileStorage.removeItem(STORAGE_KEYS.pincode)}
      >
        <Text>{t(locale, "clearPincode")}</Text>
      </Pressable>
      <Pressable
        style={styles.btn}
        onPress={() => mobileStorage.removeItem(STORAGE_KEYS.history)}
      >
        <Text>{t(locale, "clearHistory")}</Text>
      </Pressable>
      <Text style={styles.sub}>Trust feedback (beta)</Text>
      <View style={styles.row}>
        {[1, 2, 3, 4, 5].map((n) => (
          <Pressable
            key={n}
            style={styles.rateBtn}
            onPress={async () => {
              const sid = (await mobileStorage.getItem(STORAGE_KEYS.sessionId)) ?? "";
              track("trust_feedback", { sessionId: sid, rating: n });
            }}
          >
            <Text>{n}</Text>
          </Pressable>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  title: { fontSize: 22, fontWeight: "700", marginBottom: 16 },
  btn: {
    padding: 16,
    backgroundColor: colors.surface,
    borderRadius: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: colors.border,
    minHeight: touchTargetMin,
    justifyContent: "center",
  },
  sub: { marginTop: 16, fontWeight: "600" },
  row: { flexDirection: "row", gap: 8, marginTop: 8 },
  rateBtn: {
    minWidth: touchTargetMin,
    minHeight: touchTargetMin,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
  },
});
