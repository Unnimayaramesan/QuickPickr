import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        qp: {
          primary: "#0B57D0",
          bg: "#F6F7F9",
          surface: "#FFFFFF",
          text: "#111827",
          muted: "#6B7280",
          border: "#E5E7EB",
          error: "#B3261E",
          warning: "#B06000",
        },
      },
    },
  },
  plugins: [],
};
export default config;
