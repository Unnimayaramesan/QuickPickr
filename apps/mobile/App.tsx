import { useState } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { StatusBar } from "expo-status-bar";
import type { Locale, SearchHistoryEntry } from "@quickpickr/shared";
import { HomeScreen } from "./src/screens/HomeScreen";
import { HistoryScreen } from "./src/screens/HistoryScreen";
import { SettingsScreen } from "./src/screens/SettingsScreen";
import { PrivacyScreen } from "./src/screens/PrivacyScreen";

export type RootStackParamList = {
  Home: undefined;
  History: undefined;
  Settings: undefined;
  Privacy: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function App() {
  const [locale] = useState<Locale>("en");
  const [rerun, setRerun] = useState<SearchHistoryEntry | null>(null);

  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Stack.Navigator>
        <Stack.Screen name="Home" options={{ title: "QuickPickr" }}>
          {({ navigation }) => (
            <HomeScreen locale={locale} navigation={navigation} />
          )}
        </Stack.Screen>
        <Stack.Screen name="History" options={{ title: "History" }}>
          {({ navigation }) => (
            <HistoryScreen
              locale={locale}
              onRerun={(e) => {
                setRerun(e);
                navigation.navigate("Home");
              }}
            />
          )}
        </Stack.Screen>
        <Stack.Screen name="Settings" options={{ title: "Settings" }}>
          {() => <SettingsScreen locale={locale} />}
        </Stack.Screen>
        <Stack.Screen name="Privacy" options={{ title: "Privacy" }}>
          {() => <PrivacyScreen locale={locale} />}
        </Stack.Screen>
      </Stack.Navigator>
    </NavigationContainer>
  );
}
