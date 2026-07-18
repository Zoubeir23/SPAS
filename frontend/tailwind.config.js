import colors from "tailwindcss/colors"

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: "#1c41a6",
        "primary-hover": "#16348a",
        "background-light": "#f6f6f8",
        "background-dark": "#121620",
        "surface-dark": "#1e2330",
        // Semantic status colors, shared by Bouton/Badge/Alerte/Carte so every
        // component agrees on what "success"/"warning"/"danger"/"info" look like.
        success: colors.green,
        warning: colors.yellow,
        danger: colors.red,
        info: colors.blue,
      },
      fontFamily: {
        display: ["Inter", "sans-serif"],
        body: ["Inter", "sans-serif"],
      },
      borderRadius: {
        DEFAULT: "0.25rem",
        lg: "0.5rem",
        xl: "0.75rem",
        full: "9999px",
      },
      spacing: {
        // Shared layout dimensions (MiseEnPagePrincipale / BarreLaterale / EnTete)
        sidebar: "17.5rem", // 280px
        header: "4.375rem", // 70px
      },
    },
  },
  plugins: [],
}

