import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0b1220",
        slatePanel: "#111827",
        discipline: "#38bdf8",
        mutedGold: "#c8a95a"
      }
    }
  },
  plugins: []
};

export default config;
