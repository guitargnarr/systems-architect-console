/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Ibanista Brand Colors (from ibanista.com)
        brand: {
          navy: '#32373c',
          dark: '#1a1d20',
          charcoal: '#2a2e33',
        },
        // Extended palette for tools
        primary: {
          50: '#f7f8f8',
          100: '#eef0f1',
          200: '#d5dadc',
          300: '#b3bcc0',
          400: '#8a969c',
          500: '#6b7880',
          600: '#566068',
          700: '#32373c', // Brand navy
          800: '#2a2e33',
          900: '#1a1d20',
        },
        // Warm accent for CTAs (French-inspired gold/amber)
        accent: {
          50: '#fefbf3',
          100: '#fdf4e0',
          200: '#fbe8c1',
          300: '#f7d697',
          400: '#f2be5c',
          500: '#e9a235',
          600: '#d4862a',
          700: '#b06824',
          800: '#8f5324',
          900: '#754520',
        },
        // Success/positive (French countryside green)
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
      },
      fontFamily: {
        sans: ['Poppins', 'Helvetica', 'Arial', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(50, 55, 60, 0.08), 0 10px 20px -2px rgba(50, 55, 60, 0.04)',
        'medium': '0 4px 25px -5px rgba(50, 55, 60, 0.1), 0 10px 30px -5px rgba(50, 55, 60, 0.08)',
        'elevated': '0 10px 40px -10px rgba(50, 55, 60, 0.15), 0 20px 50px -15px rgba(50, 55, 60, 0.1)',
      },
    },
  },
  plugins: [],
}
