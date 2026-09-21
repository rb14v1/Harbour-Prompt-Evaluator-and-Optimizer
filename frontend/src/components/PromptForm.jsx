import { useState } from 'react'
import { Send } from 'lucide-react'
import { evaluationAPI } from '../services/api'
import LoadingSpinner from './LoadingSpinner'

export default function PromptForm({ onSuccess }) {
  const [prompt, setPrompt] = useState('')
  const [role, setRole] = useState('Software')
  const [expertise, setExpertise] = useState('Intermediate')
  const [context, setContext] = useState('Work')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!prompt.trim()) {
      setError('Please enter a prompt')
      return
    }

    setLoading(true)
    setError('')

    try {
      console.log('[PromptForm] Submitting prompt with metadata...', { role, expertise, context })
      const result = await evaluationAPI.evaluatePrompt(prompt, { role, expertise, context })
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
      <h2 className="text-2xl font-bold mb-4">Evaluate Your Prompt</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label className="label">Your Department/Role</label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="input"
            disabled={loading}
          >
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
            <option>Business Analysis</option>
            <option>Other</option>
          </select>
        </div>

        <div>
          <label className="label">Your Expertise Level</label>
          <select
            value={expertise}
            onChange={(e) => setExpertise(e.target.value)}
            className="input"
            disabled={loading}
          >
            <option>Beginner</option>
            <option>Know Basics</option>
            <option>Intermediate</option>
            <option>Advanced</option>
            <option>Expert</option>
          </select>
        </div>

        <div>
          <label className="label">Context/Place</label>
          <select
            value={context}
            onChange={(e) => setContext(e.target.value)}
            className="input"
            disabled={loading}
          >
            <option>Work</option>
            <option>Personal</option>
            <option>Research</option>
            <option>Conference</option>
            <option>Training</option>
            <option>Client Presentation</option>
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
        disabled={loading || !prompt.trim()}
        className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <LoadingSpinner /> Evaluating...
          </>
        ) : (
          <>
            <Send size={18} /> Evaluate Prompt
          </>
        )}
      </button>

      <p className="mt-3 text-sm text-gray-600 dark:text-gray-400 text-center">
        Your prompt will be evaluated across 8 quality dimensions
      </p>
    </form>
  )
}
