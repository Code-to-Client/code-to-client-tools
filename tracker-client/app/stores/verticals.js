import { defineStore } from 'pinia'

export const useVerticalsStore = defineStore('verticals', () => {
  const items = ref([])
  const loading = ref(false)

  async function fetchList() {
    loading.value = true
    try {
      const api = useApi()
      items.value = await api.get('/verticals')
    } finally {
      loading.value = false
    }
  }

  async function create(body) {
    const api = useApi()
    return api.post('/verticals', body)
  }

  async function update(id, body) {
    const api = useApi()
    return api.patch(`/verticals/${id}`, body)
  }

  async function remove(id) {
    const api = useApi()
    await api.delete(`/verticals/${id}`)
  }

  return { items, loading, fetchList, create, update, remove }
})
