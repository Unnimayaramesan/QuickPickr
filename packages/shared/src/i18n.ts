export type Locale = "en" | "hi";

const strings = {
  en: {
    appName: "QuickPickr",
    tagline: "One search. Four apps. Best price.",
    productLabel: "Product",
    productPlaceholder: "Amul Gold 500 ml",
    pincodeLabel: "Pincode",
    pincodePlaceholder: "560034",
    search: "Search",
    searching: "Searching…",
    useLocation: "Use my location",
    locationError: "Could not detect pincode from location.",
    lowestPrice: "Lowest price",
    closestMatch: "Closest match",
    stalePrice: "Price may be outdated",
    buyOn: "Buy on",
    notAvailable: "Not available at your pincode",
    temporarilyUnavailable: "Temporarily unavailable",
    trustFooter:
      "Prices sourced from Blinkit, Zepto, BigBasket, and Swiggy Instamart websites. Confirm final price at checkout.",
    history: "Recent searches",
    settings: "Settings",
    clearPincode: "Clear saved pincode",
    clearHistory: "Clear search history",
    privacy: "Privacy notice",
    noResults: "We couldn't find this item. Try a more specific name (brand + size).",
    confirmCheckout: "Price may have changed. You'll complete your order on the retailer.",
    language: "Language",
    english: "English",
    hindi: "Hindi",
  },
  hi: {
    appName: "QuickPickr",
    tagline: "एक खोज। चार ऐप। सबसे सस्ता।",
    productLabel: "उत्पाद",
    productPlaceholder: "अमूल गोल्ड 500 ml",
    pincodeLabel: "पिनकोड",
    pincodePlaceholder: "560034",
    search: "खोजें",
    searching: "खोज रहे हैं…",
    useLocation: "मेरा स्थान उपयोग करें",
    locationError: "स्थान से पिनकोड नहीं मिला।",
    lowestPrice: "सबसे कम कीमत",
    closestMatch: "निकटतम मिलान",
    stalePrice: "कीमत पुरानी हो सकती है",
    buyOn: "खरीदें",
    notAvailable: "आपके पिनकोड पर उपलब्ध नहीं",
    temporarilyUnavailable: "अस्थायी रूप से अनुपलब्ध",
    trustFooter:
      "कीमतें Blinkit, Zepto, BigBasket और Swiggy Instamart वेबसाइटों से हैं। चेकआउट पर अंतिम कीमत जांचें।",
    history: "हाल की खोज",
    settings: "सेटिंग्स",
    clearPincode: "सहेजा पिनकोड हटाएं",
    clearHistory: "खोज इतिहास हटाएं",
    privacy: "गोपनीयता सूचना",
    noResults: "यह आइटम नहीं मिला। अधिक विशिष्ट नाम आज़माएं (ब्रांड + साइज)।",
    confirmCheckout: "कीमत बदल सकती है। आप रिटेलर पर ऑर्डर पूरा करेंगे।",
    language: "भाषा",
    english: "English",
    hindi: "हिन्दी",
  },
} as const;

export type I18nKey = keyof (typeof strings)["en"];

export function t(locale: Locale, key: I18nKey): string {
  return strings[locale][key] ?? strings.en[key];
}
