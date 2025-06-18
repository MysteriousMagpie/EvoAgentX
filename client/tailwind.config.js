/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        primary: "#4F46E5",
        secondary: "#10B981",
        accent: "#F59E0B",
      },
    },
  },
  darkMode: 'class',
  plugins: [],
};
