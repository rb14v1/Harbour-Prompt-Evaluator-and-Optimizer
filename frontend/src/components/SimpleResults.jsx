import { Download, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import ScoreCard from './ScoreCard'
import DimensionChart from './DimensionChart'
import AgentPipeline from './AgentPipeline'
import AgentDetailPanel from './AgentDetailPanel'

export default function SimpleResults({ result }) {
  const [expandedAgent, setExpandedAgent] = useState(null)
  const [isExporting, setIsExporting] = useState(false)

  if (!result) return null

  const handleExportExcel = async () => {
    if (!result?.id) {
      alert('Evaluation ID not found')
      return
    }

    setIsExporting(true)
    try {
      const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
      const url = `${apiBaseUrl}/evaluations/${result.id}/export_excel/`

      const response = await fetch(url, {
        method: 'GET',
        credentials: 'include'
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.setAttribute('download', `evaluation_${result.id}.xlsx`)
      document.body.appendChild(link)
      link.click()
      link.parentNode.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    } catch (error) {
      console.error('Export failed:', error)
      alert(`Failed to export: ${error.message}`)
    } finally {
      setIsExporting(false)
    }
  }

  const executionHistory = result.execution_history
  const currentIteration = executionHistory?.iterations?.[0] || {}
  const stages = currentIteration.stages || {}

  return (
    <div className="space-y-8">
      {/* Summary Header */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg p-8 shadow-md">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-3xl font-bold">Evaluation Results</h2>
          <button
            onClick={handleExportExcel}
            disabled={isExporting}
            className="flex items-center gap-2 px-4 py-2 bg-white text-primary-600 rounded-lg font-medium hover:bg-gray-100 disabled:opacity-50 transition-colors"
          >
            <Download size={18} />
            {isExporting ? 'Exporting...' : 'Download Excel'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-sm opacity-90 mb-2">Final Score</p>
            <p className="text-5xl font-bold">{result.final_score ? result.final_score.toFixed(1) : 'N/A'}/10</p>
            <p className="text-xs opacity-75 mt-1">Threshold: 9.8</p>
          </div>
          <div>
            <p className="text-sm opacity-90 mb-2">Status</p>
            <p className="text-2xl font-bold">{result.status}</p>
            <p className="text-xs opacity-75 mt-1">Iterations: {result.iterations_required}/3</p>
          </div>
          <div>
            <p className="text-sm opacity-90 mb-2">Improvements</p>
            <p className="text-2xl font-bold">{result.improvements_made}</p>
            <p className="text-xs opacity-75 mt-1">Changes made</p>
          </div>
        </div>
      </div>

      {/* Prompts Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-3">Original Prompt</h3>
          <p className="text-sm text-gray-700 dark:text-gray-300 p-4 bg-gray-50 dark:bg-gray-800 rounded whitespace-pre-wrap">
            {result.original_prompt}
          </p>
        </div>

        {result.final_prompt !== result.original_prompt && (
          <div className="bg-white dark:bg-gray-900 rounded-lg border border-success-500 border-2 p-6">
            <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
              ✓ Improved Prompt
            </h3>
            <p className="text-sm text-gray-700 dark:text-gray-300 p-4 bg-success-50 dark:bg-success-900/20 rounded whitespace-pre-wrap">
              {result.final_prompt}
            </p>
          </div>
        )}
      </div>

      {/* Dimensions Chart */}
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-6">Quality Dimensions</h3>
        <DimensionChart scores={result.final_evaluation.dimension_scores} />
      </div>

      {/* Score Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ScoreCard
          score={result.initial_evaluation.overall_score}
          label="Initial Score"
          subtitle="Before improvements"
        />
        <ScoreCard
          score={result.final_evaluation.overall_score}
          label="Final Score"
          subtitle="After optimization"
        />
      </div>

      {/* Agent Details (Optional/Expandable) */}
      <div className="space-y-3">
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">Agent Details (Optional)</h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Click to expand and view detailed output from each agent in the pipeline
        </p>

        {['preprocessor', 'classifier', 'analyzer', 'validator', 'scoring', 'improver', 'report'].map((agent) => {
          const stageData = stages[agent]
          const isExpanded = expandedAgent === agent

          if (!stageData) return null

          return (
            <div
              key={agent}
              className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
            >
              <button
                onClick={() => setExpandedAgent(isExpanded ? null : agent)}
                className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <div className="flex items-center gap-3">
                  {isExpanded ? (
                    <ChevronUp size={20} className="text-primary-600" />
                  ) : (
                    <ChevronDown size={20} className="text-gray-400" />
                  )}
                  <span className="font-semibold text-gray-900 dark:text-gray-100 capitalize">
                    {agent === 'scoring' ? 'Scoring Engine' : agent}
                  </span>
                </div>
                <span className="text-xs px-2 py-1 bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 rounded">
                  View
                </span>
              </button>

              {isExpanded && (
                <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-800">
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {stageData.output && (
                      <div>
                        <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">Output:</p>
                        <pre className="text-xs bg-gray-100 dark:bg-gray-900 p-3 rounded overflow-x-auto text-gray-800 dark:text-gray-200">
                          {JSON.stringify(stageData.output, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Summary Section */}
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-3">Summary</h3>
        <p className="text-gray-700 dark:text-gray-300">{result.summary}</p>
      </div>
    </div>
  )
}
