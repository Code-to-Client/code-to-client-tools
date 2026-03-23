/**
 * Secondary accent color for metric numbers, nav links, etc.
 * Uses the same color options as primary. Sets --app-secondary and persists to localStorage.
 */
import { PRIMARY_COLOR_OPTIONS } from './usePrimaryColor'

const STORAGE_KEY = 'contact-form-tracker-secondary-color'
const DEFAULT_SECONDARY = '#64748b'

export const SECONDARY_COLOR_OPTIONS = PRIMARY_COLOR_OPTIONS

function applySecondary(hex) {
  if (import.meta.client && hex) {
    document.documentElement.style.setProperty('--app-secondary', hex)
  }
}

export function useSecondaryColor() {
  const secondaryColor = ref(DEFAULT_SECONDARY)

  function setSecondary(hex) {
    const value = hex || DEFAULT_SECONDARY
    secondaryColor.value = value
    applySecondary(value)
    try {
      localStorage.setItem(STORAGE_KEY, value)
    } catch (_) {}
  }

  onMounted(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored && SECONDARY_COLOR_OPTIONS.some((o) => o.value === stored)) {
        secondaryColor.value = stored
      }
    } catch (_) {}
    applySecondary(secondaryColor.value)
  })

  return {
    secondaryColor: readonly(secondaryColor),
    setSecondary,
    options: SECONDARY_COLOR_OPTIONS,
  }
}
