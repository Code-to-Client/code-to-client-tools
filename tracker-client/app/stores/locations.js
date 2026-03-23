import { defineStore } from 'pinia'

export const useLocationsStore = defineStore('locations', () => {
  const zips = ref([])
  const cityStates = ref([])
  const loading = ref(false)

  async function fetchList(vertical) {
    loading.value = true
    try {
      const api = useApi()
      const url = vertical ? `/locations?vertical=${encodeURIComponent(vertical)}` : '/locations'
      const data = await api.get(url)
      zips.value = data.zips ?? []
      cityStates.value = data.city_states ?? []
    } finally {
      loading.value = false
    }
  }

  return { zips, cityStates, loading, fetchList }
})
