import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
})

export default {
  getStats: () => api.get('/stats').then(r => r.data),
  getDiseases: () => api.get('/diseases').then(r => r.data),
  getDisease: (efoId) => api.get(`/diseases/${efoId}`).then(r => r.data),
  getGraph: (efoId) => {
    const url = efoId ? `/graph/${efoId}` : '/graph'
    return api.get(url).then(r => r.data)
  },
  compare: (d1, d2) => api.get('/compare', { params: { d1, d2 } }).then(r => r.data),
  getTarget: (symbol) => api.get(`/targets/${symbol}`).then(r => r.data),
}
