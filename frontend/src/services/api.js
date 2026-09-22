import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const TIMEOUT = import.meta.env.VITE_API_TIMEOUT || 300000

// Store configuration fetched from backend
let CONFIG = {
  threshold: 9.5,  // Default fallback
  dimensions: []
}

// Fetch configuration from backend on startup
async function fetchConfig() {
  try {
    const response = await axios.get(`${API_URL}/config/`, { timeout: 5000 })
    CONFIG = response.data
  } catch (error) {
    console.warn('Failed to fetch config from backend, using defaults:', error.message)
  }
}

// Fetch config immediately
fetchConfig()

// Export a function to get the current config
export const getConfig = () => CONFIG

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
  evaluatePrompt: async (prompt, metadata = {}) => {
    const response = await apiClient.post('/evaluations/evaluate/', {
      prompt,
      user_role: metadata.role || 'Software',
      task_type: metadata.taskType || 'Create Code',
      output_format: metadata.outputFormat || 'text',
    })
    return response.data
  },

  // Quick evaluation (no iterations, ~10-15 seconds)
  quickEvaluatePrompt: async (prompt) => {
    const response = await apiClient.post('/evaluations/quick_evaluate/', {
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
