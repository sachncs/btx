/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ink: {
          50:  '#f5f7f8',
          100: '#e8ecee',
          200: '#c7d3d7',
          300: '#9aacb3',
          400: '#6b818a',
          500: '#4a5d65',
          600: '#334149',
          700: '#232e34',
          800: '#161e23',
          900: '#0c1216',
          950: '#060a0d',
        },
        accent: {
          50:  '#ecfdf6',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#5fd0a4',
          600: '#2bb489',
          700: '#1f8d6b',
          800: '#1a6f55',
          900: '#155a47',
        },
        glow: {
          400: '#7ce2c8',
          500: '#5fd0a4',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
        display: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      letterSpacing: {
        tightest: '-0.045em',
        crisp: '-0.022em',
      },
      fontSize: {
        'display-2xl': ['clamp(3rem, 6vw + 1rem, 5.5rem)', { lineHeight: '0.98', letterSpacing: '-0.045em' }],
        'display-xl':  ['clamp(2.5rem, 4.5vw + 1rem, 4.25rem)', { lineHeight: '1.02', letterSpacing: '-0.04em' }],
        'display-lg':  ['clamp(2rem, 3vw + 1rem, 3rem)', { lineHeight: '1.06', letterSpacing: '-0.035em' }],
        'display-md':  ['clamp(1.5rem, 2vw + 1rem, 2.25rem)', { lineHeight: '1.1', letterSpacing: '-0.025em' }],
      },
      maxWidth: {
        '8xl': '88rem',
      },
      backgroundImage: {
        'grid-faint':
          'linear-gradient(to right, rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.04) 1px, transparent 1px)',
        'radial-fade':
          'radial-gradient(ellipse at top, rgba(95,208,164,0.15), transparent 60%)',
      },
      backgroundSize: {
        'grid-md': '44px 44px',
        'grid-lg': '64px 64px',
      },
      keyframes: {
        'fade-up': {
          '0%':   { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'marquee': {
          '0%':   { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        'shimmer': {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'pulse-ring': {
          '0%':   { transform: 'scale(0.9)', opacity: '0.5' },
          '100%': { transform: 'scale(2.2)', opacity: '0' },
        },
        'orbit': {
          '0%':   { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        'drift': {
          '0%, 100%': { transform: 'translate3d(0,0,0)' },
          '50%':      { transform: 'translate3d(0,-8px,0)' },
        },
        'blink': {
          '0%, 49%':  { opacity: '1' },
          '50%, 100%': { opacity: '0' },
        },
        'gradient': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%':      { backgroundPosition: '100% 50%' },
        },
      },
      animation: {
        'fade-up':    'fade-up 0.8s cubic-bezier(0.22,1,0.36,1) both',
        'fade-in':    'fade-in 0.6s ease-out both',
        'marquee':    'marquee 36s linear infinite',
        'shimmer':    'shimmer 3s linear infinite',
        'pulse-ring': 'pulse-ring 2.4s cubic-bezier(0.22,1,0.36,1) infinite',
        'orbit':      'orbit 24s linear infinite',
        'drift':      'drift 6s ease-in-out infinite',
        'blink':      'blink 1.1s steps(2) infinite',
        'gradient':   'gradient 8s ease infinite',
      },
      boxShadow: {
        'glow':     '0 0 0 1px rgba(95,208,164,0.15), 0 12px 40px -12px rgba(95,208,164,0.35)',
        'soft':     '0 1px 0 0 rgba(255,255,255,0.04) inset, 0 30px 80px -40px rgba(0,0,0,0.6)',
        'card':     '0 1px 0 0 rgba(255,255,255,0.06) inset, 0 1px 2px rgba(0,0,0,0.4), 0 30px 60px -20px rgba(0,0,0,0.6)',
        'card-hover': '0 1px 0 0 rgba(255,255,255,0.08) inset, 0 1px 2px rgba(0,0,0,0.4), 0 40px 80px -30px rgba(95,208,164,0.25)',
      },
    },
  },
  plugins: [],
};