/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ams: {
          bg: '#0a0e1a',
          surface: '#111827',
          card: '#1a2235',
          border: '#1e293b',
          accent: '#3b82f6',
          critical: '#ef4444',
          high: '#f97316',
          medium: '#eab308',
          low: '#22c55e',
          muted: '#64748b',
        },
      },
    },
  },
  plugins: [],
}
