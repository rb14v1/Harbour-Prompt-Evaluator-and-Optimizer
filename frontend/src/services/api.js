import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const TIMEOUT = import.meta.env.VITE_API_TIMEOUT || 120000

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies for session auth
})

// Add interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('[API Error]', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      message: error.message,
      code: error.code,
      url: error.config?.url,
      method: error.config?.method,
      data: error.response?.data,
      isNetworkError: !error.response,
      isTimeout: error.code === 'ECONNABORTED',
    })

    if (error.response?.status === 401) {
      console.error('Unauthorized - user not authenticated')
    }

    return Promise.reject(error)
  }
)

export const evaluationAPI = {
  // Submit a single prompt for evaluation
  evaluatePrompt: async (prompt) => {
    const response = await apiClient.post('/evaluations/evaluate/', {
      prompt,
    })
    return response.data
  },

  // Batch evaluate multiple prompts
  batchEvaluate: async (prompts) => {
    const response = await apiClient.post('/evaluations/batch_evaluate/', {
      prompts,
    })
    return response.data
  },

  // Get evaluation details
  getEvaluationDetail: async (id) => {
    const response = await apiClient.get(`/evaluations/${id}/detail/`)
    return response.data
  },

  // Get user's prompt history
  getHistory: async () => {
    const response = await apiClient.get('/history/')
    return response.data
  },

  // Get evaluations for a specific prompt
  getPromptEvaluations: async (promptId) => {
    const response = await apiClient.get(`/history/${promptId}/evaluations/`)
    return response.data
  },

  // Get user statistics
  getStats: async () => {
    const response = await apiClient.get('/history/stats/')
    return response.data
  },

  // Health check
  healthCheck: async () => {
    const response = await apiClient.get('/health/')
    return response.data
  },
}

export default apiClient
