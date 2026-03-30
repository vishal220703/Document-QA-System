import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#0D1321",
        surf: "#F4F7F5",
        mint: "#7A9E9F",
        clay: "#D8A47F"
      },
      boxShadow: {
        soft: "0 20px 45px rgba(13, 19, 33, 0.15)"
      }
    }
  },
  plugins: []
};

export default config;
