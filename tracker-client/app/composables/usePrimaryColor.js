/**
 * Primary color preference for Element Plus and app accents.
 * Sets --el-color-primary on <html> and persists to localStorage.
 */
const STORAGE_KEY = 'contact-form-tracker-primary-color'
const DEFAULT_PRIMARY = '#409eff'

export const PRIMARY_COLOR_OPTIONS = [
  { value: '#409eff', label: 'Blue' },
  { value: '#67c23a', label: 'Green' },
  { value: '#9c27b0', label: 'Purple' },
  { value: '#ea580c', label: 'Orange' },
  { value: '#009688', label: 'Teal' },
  { value: '#f56c6c', label: 'Rose' },
  { value: '#0ea5e9', label: 'Sky' },
  { value: '#8b5cf6', label: 'Violet' },
  { value: '#059669', label: 'Emerald' },
  { value: '#6366f1', label: 'Indigo' },
  { value: '#4f46e5', label: 'Indigo (deep)' },
  { value: '#06b6d4', label: 'Cyan' },
  { value: '#d946ef', label: 'Fuchsia' },
  { value: '#ec4899', label: 'Pink' },
  { value: '#ca8a04', label: 'Amber' },
  { value: '#84cc16', label: 'Lime' },
  { value: '#ef4444', label: 'Red' },
  { value: '#64748b', label: 'Slate' },
  { value: '#6b7280', label: 'Gray' },
  { value: '#57534e', label: 'Stone' },
]

function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result
    ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}`
    : '64, 158, 255'
}

function applyPrimary(hex) {
  if (import.meta.client && hex) {
    document.documentElement.style.setProperty('--el-color-primary', hex)
    document.documentElement.style.setProperty('--el-color-primary-rgb', hexToRgb(hex))
  }
}

export function usePrimaryColor() {
  const primaryColor = ref(DEFAULT_PRIMARY)

  function setPrimary(hex) {
    const value = hex || DEFAULT_PRIMARY
    primaryColor.value = value
    applyPrimary(value)
    try {
      localStorage.setItem(STORAGE_KEY, value)
    } catch (_) {}
  }

  onMounted(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored && PRIMARY_COLOR_OPTIONS.some((opt) => opt.value === stored)) {
        primaryColor.value = stored
      }
    } catch (_) {}
    applyPrimary(primaryColor.value)
  })

  return {
    primaryColor: readonly(primaryColor),
    setPrimary,
    options: PRIMARY_COLOR_OPTIONS,
  }
}
