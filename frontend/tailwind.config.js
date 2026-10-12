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
          ivory: '#F7F5F0',    // Warm ivory background
          teal: '#183C43',     // Deep teal primary
          tealHover: '#122D33',
          mint: '#B9DED4',     // Soft mint accent
          coral: '#D87763',    // Muted coral accent
          charcoal: '#272D2B', // Charcoal text
          surface: '#FFFFFF',  // White content surface
          border: '#E3DFD5',   // Gentle border
          muted: '#68726F',    // Secondary muted text
          badge: '#EBF5F2',    // Subtle mint tinted pill
        },
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'Noto Sans Devanagari', 'system-ui', 'sans-serif'],
        devanagari: ['Noto Sans Devanagari', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(24, 60, 67, 0.06)',
        'elevated': '0 12px 32px -4px rgba(24, 60, 67, 0.10)',
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
