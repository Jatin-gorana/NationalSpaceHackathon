/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'space-dark': '#0a0e27',
        'space-blue': '#1e3a8a',
        'neon-cyan': '#00ffff',
        'neon-green': '#00ff00',
        'warning-red': '#ff0000',
      },
    },
  },
  plugins: [],
}
