import { defineStore } from 'pinia'

export const STATUS_LABELS = {
  CONTACTED: 'Contacted',
  DESIGN_PARTNER_PROSPECT: 'Design Partner Prospect',
  WAITLISTED: 'Waitlisted',
  OTHER_PROSPECT: 'Other Prospect',
  DISCOVERY_CALL: 'Discovery Call',
  DESIGN_PARTNER: 'Design Partner',
  CUSTOMER: 'Customer',
  NOT_INTERESTED: 'Not Interested',
}

/** Single source of truth for status colors (dashboard cards + contact status badges). Grouped by pipeline stage: grey=no reply, blue=responded, purple=engaged, green=won, red=lost. */
export const STATUS_COLORS = {
  CONTACTED: '#6b7280',              // grey — no response yet
  DESIGN_PARTNER_PROSPECT: '#2563eb', // blue — responded
  WAITLISTED: '#2563eb',             // blue — responded
  OTHER_PROSPECT: '#2563eb',         // blue — responded
  DISCOVERY_CALL: '#7c3aed',         // purple — active engagement
  DESIGN_PARTNER: '#22c55e',         // green — won
  CUSTOMER: '#22c55e',               // green — won
  NOT_INTERESTED: '#b91c1c',         // red — lost
}

export const useContactsStore = defineStore('contacts', () => {
  const items = ref([])
  const loading = ref(false)

  async function fetchList(params = {}) {
    loading.value = true
    try {
      const api = useApi()
      const q = new URLSearchParams()
      if (params.status) q.set('status', params.status)
      if (params.vertical) q.set('vertical', params.vertical)
      if (params.postal_code) q.set('postal_code', params.postal_code)
      if (params.city_state) q.set('city_state', params.city_state)
      if (params.limit) q.set('limit', String(params.limit))
      if (params.offset) q.set('offset', String(params.offset))
      const query = q.toString()
      items.value = await api.get(`/contacts${query ? `?${query}` : ''}`)
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id) {
    const api = useApi()
    return api.get(`/contacts/${id}`)
  }

  async function create(body) {
    const api = useApi()
    return api.post('/contacts', body)
  }

  async function update(id, body) {
    const api = useApi()
    return api.patch(`/contacts/${id}`, body)
  }

  async function remove(id) {
    const api = useApi()
    await api.delete(`/contacts/${id}`)
  }

  return { items, loading, fetchList, fetchOne, create, update, remove }
})
