/**
 * Light/dark mode toggle for Element Plus + UnoCSS.
 * Toggles the `dark` class on <html> so Element Plus and dark: utilities switch together.
 * Persists preference in localStorage.
 */
const STORAGE_KEY = 'contact-form-tracker-dark'

export function useDark() {
  const isDark = ref(false)

  function apply(dark) {
    if (import.meta.client) {
      if (dark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
      try {
        localStorage.setItem(STORAGE_KEY, dark ? '1' : '0')
      } catch (_) {}
    }
    isDark.value = !!dark
  }

  function toggle() {
    apply(!isDark.value)
  }

  onMounted(() => {
    let preferDark = false
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored !== null) preferDark = stored === '1'
      else preferDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    } catch (_) {}
    apply(preferDark)
  })

  return { isDark: readonly(isDark), toggle, apply }
}
