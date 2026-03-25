/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        'bg-dark':  '#0B0F14',
        'bg-card':  '#111827',
        'bg-card2': '#0D1520',
        'neon':     '#00E5FF',
        'purple':   '#7C3AED',
        'muted':    '#6B7280',
        'text':     '#E5E7EB',
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'monospace'],
        display: ['"Orbitron"', 'sans-serif'],
        body: ['"Exo 2"', 'sans-serif'],
      },
      animation: {
        pulse2: 'pulse2 2s ease-in-out infinite',
        shimmer: 'shimmer 2s linear infinite',
        fadein: 'fadein 0.5s ease',
        glow: 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        pulse2: {
          '0%, 100%': { opacity: 1 },
          '50%':      { opacity: 0.4 },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition:  '200% 0' },
        },
        fadein: {
          from: { opacity: 0, transform: 'translateY(8px)' },
          to:   { opacity: 1, transform: 'translateY(0)' },
        },
        glow: {
          from: { boxShadow: '0 0 6px #00E5FF44, 0 0 12px #00E5FF22' },
          to:   { boxShadow: '0 0 16px #00E5FFaa, 0 0 32px #00E5FF55' },
        },
      },
      boxShadow: {
        neon:       '0 0 10px #00E5FF88, 0 0 20px #00E5FF33',
        'neon-lg':  '0 0 20px #00E5FFaa, 0 0 40px #00E5FF55',
        purple:     '0 0 10px #7C3AED88',
        card:       '0 2px 24px rgba(0,0,0,0.5)',
      },
    },
  },
  plugins: [],
}
