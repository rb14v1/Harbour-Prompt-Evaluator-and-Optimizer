/**
 * Claude vs Project Comparison Page
 * Place in: frontend/src/pages/ComparePrompts.jsx
 *
 * Simple, calm UI design with Tailwind CSS
 * Compares Claude and Project improvements side-by-side
 */

import { useState } from 'react'
import { Download, Loader } from 'lucide-react'
import axios from 'axios'

const DIMENSIONS = [
  { name: 'Clarity', key: 'clarity' },
  { name: 'Specificity', key: 'specificity' },
  { name: 'Context', key: 'context' },
  { name: 'Completeness', key: 'completeness' },
  { name: 'Requirements', key: 'requirements' },
  { name: 'Constraints', key: 'constraints' },
  { name: 'Expected Output', key: 'expected_output' },
  { name: 'Actionability', key: 'actionability' }
]

export default function ComparePrompts() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const handleCompare = async (e) => {
    e.preventDefault()

    if (!prompt.trim()) {
      setError('Please enter a prompt')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await axios.post('http://localhost:3001/api/compare-prompt', {
        prompt: prompt.trim()
      })

      setResult(response.data)
    } catch (err) {
      setError(err.message || 'Failed to compare prompts. Make sure the Node.js backend is running on port 3001.')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadExcel = async () => {
    try {
      const response = await axios.post(
        'http://localhost:3001/api/download-excel',
        result,
        { responseType: 'blob' }
      )

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `prompt-comparison-${new Date().getTime()}.xlsx`)
      document.body.appendChild(link)
      link.click()
      link.parentChild.removeChild(link)
    } catch (err) {
      setError('Failed to download Excel file')
    }
  }

  const getScoreColor = (score) => {
    if (score >= 8.5) return 'text-green-600 dark:text-green-400'
    if (score >= 7) return 'text-blue-600 dark:text-blue-400'
    if (score >= 5) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-red-600 dark:text-red-400'
  }

  const getWinner = (claudeScore, projectScore) => {
    if (Math.abs(claudeScore - projectScore) < 0.1) return 'Tie'
    return claudeScore > projectScore ? 'Claude' : 'Project'
  }

  if (!result) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-gray-900 dark:to-gray-800 py-12">
        <div className="max-w-2xl mx-auto px-4">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
              Claude vs Project
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Compare prompt improvements from Claude and your project agents
            </p>
          </div>

          {/* Form */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
            <form onSubmit={handleCompare} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  Enter your prompt
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Type or paste your prompt here..."
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  rows="6"
                  disabled={loading}
                />
              </div>

              {error && (
                <div className="p-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg text-red-700 dark:text-red-200 text-sm">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading || !prompt.trim()}
                className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader size={18} className="animate-spin" />
                    Comparing...
                  </>
                ) : (
                  'Compare Improvements'
                )}
              </button>

              <p className="text-center text-sm text-gray-500 dark:text-gray-400">
                Both Claude and your project will improve this prompt, then scores will be compared across 8 dimensions.
              </p>
            </form>
          </div>

          {/* Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Claude Path</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Pure LLM improvement with 8-dimension awareness</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Project Path</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Structured pipeline with your Improver Agent</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Results View
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-gray-900 dark:to-gray-800 py-12">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Comparison Results
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Original: "{result.user_prompt}"
          </p>
        </div>

        {/* Scores Table */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden mb-8">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
                  <th className="px-6 py-4 text-left font-semibold">Dimension</th>
                  <th className="px-6 py-4 text-center font-semibold">Claude</th>
                  <th className="px-6 py-4 text-center font-semibold">Project</th>
                  <th className="px-6 py-4 text-center font-semibold">Difference</th>
                  <th className="px-6 py-4 text-center font-semibold">Winner</th>
                </tr>
              </thead>
              <tbody>
                {DIMENSIONS.map((dim, idx) => {
                  const claudeScore = result.claude.scores[dim.key] || 0
                  const projectScore = result.project.scores[dim.key] || 0
                  const diff = (claudeScore - projectScore).toFixed(2)
                  const winner = getWinner(claudeScore, projectScore)

                  return (
                    <tr
                      key={idx}
                      className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                      <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">
                        {dim.name}
                      </td>
                      <td className={`px-6 py-4 text-center font-bold ${getScoreColor(claudeScore)}`}>
                        {claudeScore.toFixed(1)}
                      </td>
                      <td className={`px-6 py-4 text-center font-bold ${getScoreColor(projectScore)}`}>
                        {projectScore.toFixed(1)}
                      </td>
                      <td className="px-6 py-4 text-center text-gray-600 dark:text-gray-400">
                        {diff > 0 ? '+' : ''}{diff}
                      </td>
                      <td className="px-6 py-4 text-center font-semibold">
                        <span className={winner === 'Claude' ? 'text-blue-600 dark:text-blue-400' : winner === 'Project' ? 'text-purple-600 dark:text-purple-400' : 'text-gray-600 dark:text-gray-400'}>
                          {winner}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          {/* Overall Scores */}
          <div className="bg-gray-50 dark:bg-gray-700 px-6 py-6 grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Overall Score</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">Comparison</p>
            </div>
            <div className="text-center border-l border-r border-gray-200 dark:border-gray-600">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Claude</p>
              <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                {result.claude.overall_score.toFixed(1)}/10
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Project</p>
              <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                {result.project.overall_score.toFixed(1)}/10
              </p>
            </div>
          </div>
        </div>

        {/* Improved Prompts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Claude */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-blue-600"></span>
              Claude Improved
            </h3>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 text-gray-700 dark:text-gray-300 text-sm leading-relaxed max-h-64 overflow-y-auto">
              {result.claude.improved_prompt}
            </div>
          </div>

          {/* Project */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-purple-600"></span>
              Project Improved
            </h3>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 text-gray-700 dark:text-gray-300 text-sm leading-relaxed max-h-64 overflow-y-auto">
              {result.project.improved_prompt}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4 justify-center">
          <button
            onClick={handleDownloadExcel}
            className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg flex items-center gap-2 transition-colors shadow-lg"
          >
            <Download size={18} />
            Download Excel
          </button>
          <button
            onClick={() => {
              setResult(null)
              setPrompt('')
            }}
            className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-lg transition-colors shadow-lg"
          >
            Compare Another
          </button>
        </div>
      </div>
    </div>
  )
}
