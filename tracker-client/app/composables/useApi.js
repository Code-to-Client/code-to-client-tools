/**
 * API client for the Contact Form Tracker backend.
 * Uses runtime config for the base URL.
 */
export function useApi() {
  const config = useRuntimeConfig()
  const baseUrl = config.public.apiBaseUrl

  async function fetchApi(path, options = {}) {
    const url = path.startsWith('http') ? path : `${baseUrl}${path}`
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(err.detail || res.statusText)
    }
    if (res.status === 204) return undefined
    return res.json()
  }

  return {
    get: (path) => fetchApi(path, { method: 'GET' }),
    post: (path, body) => fetchApi(path, { method: 'POST', body: JSON.stringify(body) }),
    patch: (path, body) => fetchApi(path, { method: 'PATCH', body: JSON.stringify(body) }),
    delete: (path) => fetchApi(path, { method: 'DELETE' }),
  }
}
