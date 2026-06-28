module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#08090c",
          900: "#0c0e13",
          850: "#11141b",
          800: "#161a23",
          700: "#1f2533",
          600: "#2a3142",
          500: "#3a4258",
        },
        signal: {
          DEFAULT: "#e63946", // damage / alert
          soft: "#f06a73",
        },
        steel: {
          50: "#eef2f7",
          100: "#dbe2ec",
          200: "#b8c2d3",
          300: "#8a96ad",
          400: "#5a6478",
          500: "#3e475a",
        },
        amber400: "#fbbf24",
        emerald400: "#34d399",
      },
      fontFamily: {
        sans: [
          '"IBM Plex Sans"',
          "ui-sans-serif",
          "system-ui",
          "sans-serif",
        ],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
      boxShadow: {
        panel: "0 1px 0 rgba(255,255,255,0.04) inset, 0 8px 24px rgba(0,0,0,0.5)",
      },
    },
  },
  plugins: [],
};
