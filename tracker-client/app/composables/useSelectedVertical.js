/**
 * Shared vertical filter persistence across Dashboard and Contacts.
 * Both pages read/write the same localStorage key so the selected vertical
 * is remembered when switching between them.
 */
const SELECTED_VERTICAL_KEY = 'outreach-tracker-dashboard-vertical'

export function useSelectedVerticalKey() {
  return SELECTED_VERTICAL_KEY
}

export function useSelectedVertical() {
  const key = SELECTED_VERTICAL_KEY
  return {
    key,
    get() {
      if (import.meta.client) {
        const saved = localStorage.getItem(key)
        if (saved == null || saved === '' || saved === '__all__') return ''
        return saved
      }
      return ''
    },
    set(value) {
      if (import.meta.client) {
        if (value) {
          localStorage.setItem(key, value)
        } else {
          localStorage.removeItem(key)
        }
      }
    },
  }
}
