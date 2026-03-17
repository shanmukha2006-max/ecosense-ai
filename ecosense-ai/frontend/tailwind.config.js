/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        mono: ['\"JetBrains Mono\"', 'monospace'],
      },
      colors: {
        background: '#020b18',
        accent: '#06b6d4',
        status: {
          green: '#22c55e',
          amber: '#f59e0b',
          red: '#ef4444',
          critical: '#7f1d1d',
        },
      },
      borderRadius: {
        card: '12px',
      },
    },
  },
  plugins: [],
};

