/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        clarity: {
          ivory: '#F5F5F5',    // Warm ivory background
          teal: '#D24726',     // Deep teal primary
          tealHover: '#AD351B',
          mint: '#FFF3EE',     // Soft mint accent
          coral: '#D24726',    // Muted coral accent
          charcoal: '#1C1C1E', // Charcoal text
          surface: '#FFFFFF',  // White content surface
          border: '#E5E5E8',   // Gentle border
          muted: '#62626A',    // Secondary muted text
          badge: '#FFF3EE',    // Subtle mint tinted pill
        },
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'Noto Sans Devanagari', 'system-ui', 'sans-serif'],
        devanagari: ['Noto Sans Devanagari', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(28, 28, 30, 0.03)',
        'elevated': '0 12px 32px -4px rgba(28, 28, 30, 0.08)',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.25rem',
        '3xl': '1.75rem',
      }
    },
  },
  plugins: [],
}
