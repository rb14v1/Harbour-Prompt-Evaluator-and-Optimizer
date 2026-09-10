import { useState } from 'react'
import { Send } from 'lucide-react'
import { evaluationAPI } from '../services/api'
import LoadingSpinner from './LoadingSpinner'

export default function PromptForm({ onSuccess }) {
  const [prompt, setPrompt] = useState('')
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
      const result = await evaluationAPI.evaluatePrompt(prompt)
      onSuccess(result)
      setPrompt('')
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Error evaluating prompt')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h2 className="text-2xl font-bold mb-4">Evaluate Your Prompt</h2>

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
