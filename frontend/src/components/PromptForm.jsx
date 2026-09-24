import { useState } from 'react'
import { Send } from 'lucide-react'
import { evaluationAPI } from '../services/api'
import LoadingSpinner from './LoadingSpinner'

export default function PromptForm({ onSuccess }) {
  const [prompt, setPrompt] = useState('')
  const [role, setRole] = useState('')
  const [taskType, setTaskType] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!role) {
      setError('Please select your Department/Role')
      return
    }

    if (!taskType) {
      setError('Please select a Task Type')
      return
    }

    if (!prompt.trim()) {
      setError('Please enter a prompt')
      return
    }

    setLoading(true)
    setError('')

    try {
      console.log('[PromptForm] Submitting evaluation...')
      const result = await evaluationAPI.evaluatePrompt(prompt, { role, taskType })
      console.log('[PromptForm] Success! Result:', result)
      onSuccess(result)
      setPrompt('')
    } catch (err) {
      console.error('[PromptForm] Error caught:', err)
      let errorMessage = 'Error evaluating prompt'

      if (!err.response) {
        errorMessage = `Network error: ${err.message || 'Unable to connect to backend'}`
      } else if (err.response.status === 401) {
        errorMessage = 'Unauthorized - please authenticate'
      } else if (err.response.status === 500) {
        errorMessage = 'Server error - backend may have crashed'
      } else if (err.response.data?.error) {
        errorMessage = err.response.data.error
      } else {
        errorMessage = err.message || 'Unknown error occurred'
      }

      console.error('[PromptForm] Final error message:', errorMessage)
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h2 className="text-2xl font-bold mb-4">Evaluate Your Prompt    [Output format is in Text]</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="label">Your Department/Role</label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="input"
            disabled={loading}
          >
            <option value="">-- Select --</option>
            <option>Software</option>
            <option>Communication</option>
            <option>Design</option>
            <option>Engineering</option>
            <option>Finance</option>
            <option>Human Resources</option>
            <option>Learning and Development</option>
            <option>Marketing</option>
            <option>Product Management</option>
            <option>Support</option>
            <option>Commercial</option>
            <option>Delivery Management</option>
            <option>Business Analysis</option>
          </select>
        </div>

        <div>
          <label className="label">Task Type</label>
          <select
            value={taskType}
            onChange={(e) => setTaskType(e.target.value)}
            className="input"
            disabled={loading}
          >
            <option value="">-- Select --</option>
            <option>Create Content</option>
            <option>Research</option>
            <option>Deep Research / Analysis</option>
            <option>Plan and Organize</option>
            <option>Ideate / Brainstorm</option>
            <option>Summarize / Review</option>
            <option>Explain / Teach</option>
            <option>Optimize / Improve</option>
          </select>
        </div>
      </div>

      <div className="mb-4">
        <label className="label">Enter Prompt</label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe what you want your prompt to do..."
          className="input h-32 resize-none"
          disabled={loading}
        />
      </div>

      {error && (
        <div className="mb-4 p-3 bg-danger-100 dark:bg-danger-900 text-danger-700 dark:text-danger-200 rounded-lg text-sm">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={loading || !prompt.trim() || !role || !taskType}
        className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <LoadingSpinner /> Evaluating with AI agents... 
          </>
        ) : (
          <>
            <Send size={18} /> Evaluate & Optimize
          </>
        )}
      </button>

      

      <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 text-center">
        Your prompt will be evaluated across 8 quality dimensions
      </p>

      <p className="mt-2 text-xs text-gray-500 dark:text-gray-500 text-center">
        • Clarity • Specificity • Context • Completeness • Requirements • Constraints • Expected Output • Actionability
      </p>
    </form>
  )
}
