import { ScrollView, StyleSheet, Text } from "react-native";
import { colors } from "@quickpickr/design-tokens";
import { t, type Locale } from "@quickpickr/shared";

export function PrivacyScreen({ locale }: { locale: Locale }) {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>{t(locale, "privacy")}</Text>
      <Text style={styles.body}>
        QuickPickr v1 stores your pincode and search history on this device only. We send
        product queries to our API to retrieve indexed public prices. No account is required.
        Purchases complete on retailer apps under their privacy policies.
      </Text>
      <Text style={styles.body}>{t(locale, "trustFooter")}</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  title: { fontSize: 22, fontWeight: "700", marginBottom: 16 },
  body: { color: colors.textMuted, marginBottom: 12, lineHeight: 22 },
});
