import { defineStore } from 'pinia'

export const useDashboardStore = defineStore('dashboard', () => {
  const data = ref(null)
  const loading = ref(false)

  async function fetch(params = {}) {
    loading.value = true
    try {
      const api = useApi()
      const q = new URLSearchParams()
      if (params.vertical) q.set('vertical', params.vertical)
      if (params.postal_code) q.set('postal_code', params.postal_code)
      if (params.city_state) q.set('city_state', params.city_state)
      const query = q.toString()
      data.value = await api.get(`/dashboard${query ? `?${query}` : ''}`)
    } finally {
      loading.value = false
    }
  }

  return { data, loading, fetch }
})
