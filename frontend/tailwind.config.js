/** Colors are CSS-variable driven so the same class names adapt to light/dark.
 *  Channels live in src/index.css (:root = dark default, html.light = light overrides). */
const v = (name) => `rgb(var(${name}) / <alpha-value>)`;

module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        ink: {
          950: v("--ink-950"),
          900: v("--ink-900"),
          850: v("--ink-850"),
          800: v("--ink-800"),
          700: v("--ink-700"),
          600: v("--ink-600"),
          500: v("--ink-500"),
        },
        signal: {
          DEFAULT: v("--signal"),
          soft: v("--signal-soft"),
        },
        steel: {
          50: v("--steel-50"),
          100: v("--steel-100"),
          200: v("--steel-200"),
          300: v("--steel-300"),
          400: v("--steel-400"),
          500: v("--steel-500"),
        },
        white: v("--white"),
        amber400: v("--amber400"),
        emerald400: v("--emerald400"),
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
