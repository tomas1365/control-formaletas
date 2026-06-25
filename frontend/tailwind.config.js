/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        steel: {
          50:  "#f0f4f8",
          100: "#d9e2ec",
          200: "#bcccdc",
          400: "#627d98",
          600: "#334e68",
          800: "#102a43",
          900: "#0a1628",
        },
        amber: {
          400: "#fbbf24",
          500: "#f59e0b",
        },
        danger: "#ef4444",
        ok:     "#22c55e",
      },
      fontFamily: {
        display: ["'Inter'", "system-ui", "sans-serif"],
        mono:    ["'JetBrains Mono'", "monospace"],
      },
    },
  },
  plugins: [],
};
