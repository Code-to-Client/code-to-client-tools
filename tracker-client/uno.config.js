import { defineConfig, presetWind } from 'unocss'

/**
 * UnoCSS config: Tailwind-compatible utilities + palette aligned with Element Plus.
 * Customize theme colors and shortcuts here; for deeper Element Plus theming,
 * override CSS variables in app/assets/css/main.css.
 */
export default defineConfig({
  presets: [presetWind()],
  // Class-based dark mode so dark: variants follow Element Plus dark toggle
  darkMode: 'class',
  theme: {
    colors: {
      // Mirror Element Plus semantic colors for layout/tweaks
      primary: '#409eff',
      success: '#67c23a',
      danger: '#f56c6c',
      warning: '#e6a23c',
      info: '#909399',
      // Neutral grays
      gray: {
        50: '#fafafa',
        100: '#f5f5f5',
        200: '#eeeeee',
        300: '#e0e0e0',
        400: '#bdbdbd',
        500: '#9e9e9e',
        600: '#757575',
        700: '#616161',
      800: '#424242',
      900: '#212121',
      950: '#171717',
      },
    },
  },
  shortcuts: {
    // Layout & spacing
    'page-container': 'min-h-screen',
    'page-content': 'max-w-6xl mx-auto px-4 sm:px-6 py-8',
    'nav-bar': 'sticky top-0 z-10 py-3 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shadow-sm',
    'nav-bar-inner': 'w-full max-w-6xl mx-auto px-4 sm:px-6 flex items-center gap-6',
    'nav-links': 'flex items-center gap-1',
    'nav-link': 'px-3 py-2 rounded-md text-gray-600 dark:text-gray-300 hover:text-primary hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors no-underline text-sm font-medium',
    'nav-link-active': 'text-primary bg-gray-100 dark:bg-gray-800 font-semibold',
    // Semantic text/links (use with Element Plus for consistency)
    'link': 'text-primary hover:underline',
    'link-muted': 'text-gray-600 dark:text-gray-400 hover:underline',
    // Cards/sections
    'card': 'rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-sm overflow-hidden',
    'card-body': 'p-5',
  },
})
