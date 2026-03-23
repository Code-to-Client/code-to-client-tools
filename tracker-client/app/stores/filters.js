import { defineStore } from 'pinia'

const KEYS = {
  vertical: 'tracker-vertical',
  zip: 'tracker-zip',
  cityState: 'tracker-city-state',
}

function load(key) {
  if (import.meta.client) return localStorage.getItem(key) || ''
  return ''
}

function save(key, value) {
  if (import.meta.client) {
    if (value) localStorage.setItem(key, value)
    else localStorage.removeItem(key)
  }
}

export const useFiltersStore = defineStore('filters', () => {
  const vertical = ref(load(KEYS.vertical))
  const zip = ref(load(KEYS.zip))
  const cityState = ref(load(KEYS.cityState))

  watch(vertical, v => save(KEYS.vertical, v))
  watch(zip, v => save(KEYS.zip, v))
  watch(cityState, v => save(KEYS.cityState, v))

  return { vertical, zip, cityState }
})
