import { Check, AlertCircle, RefreshCw, Download } from 'lucide-react'
import { useState, useEffect } from 'react'
import ScoreCard from './ScoreCard'
import DimensionChart from './DimensionChart'
import AgentPipeline from './AgentPipeline'
import AgentDetailPanel from './AgentDetailPanel'
import IterationTabs from './IterationTabs'
import TabInterface from './TabInterface'
import TableDisplay from './TableDisplay'
import JsonDisplay from './JsonDisplay'
import apiClient from '../services/api'

export default function EvaluationResult({ result, isLoading = false }) {
  const [activeAgent, setActiveAgent] = useState('preprocessor')
  const [activeIteration, setActiveIteration] = useState(0)
  const [viewMode, setViewMode] = useState('text')
  const [isExporting, setIsExporting] = useState(false)
  const [THRESHOLD, setThreshold] = useState(7.0)

  useEffect(() => {
    // Fetch threshold from backend config
    const fetchConfig = async () => {
      try {
        const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
        const response = await fetch(`${apiBaseUrl}/config/`)
        const config = await response.json()
        setThreshold(config.threshold)
      } catch (error) {
        console.log('Using default threshold:', 7.0)
        setThreshold(7.0)
      }
    }
    fetchConfig()
  }, [])

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
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
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
      alert(`Failed to export to Excel: ${error.message}`)
    } finally {
      setIsExporting(false)
    }
  }

  if (!result) return null

  const executionHistory = result.execution_history || { iterations: [] }
  const currentIteration = executionHistory.iterations?.[0] || {}
  const stages = currentIteration.stages || {}

  const statusIcon = result.status === 'Ready' ? <Check className="text-success-500" /> : <AlertCircle className="text-warning-500" />
  const statusColor = result.status === 'Ready' ? 'bg-success-100 dark:bg-success-900 text-success-800 dark:text-success-200' : 'bg-warning-100 dark:bg-warning-900 text-warning-800 dark:text-warning-200'

  return (
    <div className="space-y-6">
      {/* Header with Status & Score */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg p-6 shadow-md">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h2 className="text-2xl font-bold mb-2">Evaluation Pipeline Inspector</h2>
            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${statusColor}`}>
              {statusIcon}
              {result.status}
            </div>
          </div>
          <div className="flex flex-col items-end gap-3">
            <button
              onClick={handleExportExcel}
              disabled={isExporting}
              className="flex items-center gap-2 px-4 py-2 bg-white text-primary-600 rounded-lg font-medium hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Download size={18} />
              {isExporting ? 'Exporting...' : 'Download Excel'}
            </button>
            <div className="text-right">
              <p className="text-sm opacity-90 mb-1">Final Score</p>
              <p className="text-4xl font-bold">{result.final_score ? result.final_score.toFixed(2) : 'N/A'}/10</p>
              <p className="text-xs opacity-75 mt-1">Threshold: {THRESHOLD}</p>
            </div>
          </div>
        </div>

        <div className="mt-4 flex gap-4 text-sm">
          <div>
            <p className="opacity-75">Iterations</p>
            <p className="font-semibold">{result.iterations_required}/3</p>
          </div>
          <div>
            <p className="opacity-75">Improvements</p>
            <p className="font-semibold">{result.improvements_made}</p>
          </div>
        </div>
      </div>

      {/* Iteration Tabs */}
      {executionHistory.iterations && executionHistory.iterations.length > 0 && (
        <IterationTabs
          iterations={executionHistory.iterations}
          activeIteration={activeIteration}
          onIterationChange={setActiveIteration}
        />
      )}

      {/* Summary Section */}
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-3">Summary</h3>
        <p className="text-gray-700 dark:text-gray-300 mb-4">{result.summary}</p>

        {result.improvements_made > 0 && (
          <div className="bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-700 p-3 rounded-lg flex items-start gap-2">
            <RefreshCw size={18} className="text-primary-600 dark:text-primary-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-primary-900 dark:text-primary-100">
                Prompt improved {result.improvements_made} time(s)
              </p>
              <p className="text-sm text-primary-800 dark:text-primary-200">
                Required {result.iterations_required} iteration(s) to reach quality threshold
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Metadata Section */}
      {(result.user_role || result.task_type) && (
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">Evaluation Metadata</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {result.user_role && (
              <div className="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4 border border-primary-200 dark:border-primary-700">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Department / Role</p>
                <p className="text-lg font-semibold text-primary-700 dark:text-primary-300">
                  {result.user_role.replace(/_/g, ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                </p>
              </div>
            )}
            {result.task_type && (
              <div className="bg-success-50 dark:bg-success-900/20 rounded-lg p-4 border border-success-200 dark:border-success-700">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Task Type</p>
                <p className="text-lg font-semibold text-success-700 dark:text-success-300">
                  {result.task_type.replace(/_/g, ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Original vs Final Prompt */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-3">Original Prompt</h3>
          <p className="text-sm text-gray-700 dark:text-gray-300 p-3 bg-gray-50 dark:bg-gray-800 rounded whitespace-pre-wrap">
            {result.original_prompt}
          </p>
        </div>

        <div className="bg-white dark:bg-gray-900 rounded-lg border border-success-500 border-2 p-6">
          <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-3">✓ Final Prompt</h3>
          <p className="text-sm text-gray-700 dark:text-gray-300 p-3 bg-success-50 dark:bg-success-900/20 rounded whitespace-pre-wrap">
            {result.final_prompt}
          </p>
        </div>
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

      {/* Dimensions Chart */}
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-6">Quality Dimensions</h3>
        <DimensionChart scores={result.final_evaluation.dimension_scores} />
      </div>

      {/* Main View Tabs - JSON vs Text */}
      <TabInterface activeTab={viewMode} onTabChange={setViewMode}>
        {viewMode === 'text' ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left: Agent Pipeline */}
              <div className="lg:col-span-1">
                <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                  <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">Pipeline</h3>
                  <AgentPipeline
                    executionHistory={executionHistory}
                    activeAgent={activeAgent}
                    onAgentSelect={setActiveAgent}
                    activeIteration={activeIteration}
                  />
                </div>
              </div>

              {/* Right: Agent Detail Panel */}
              <div className="lg:col-span-2">
                <AgentDetailPanel
                  stages={stages}
                  activeAgent={activeAgent}
                  threshold={THRESHOLD}
                />
              </div>
            </div>
          </div>
        ) : (
          <JsonDisplay data={result} />
        )}
      </TabInterface>
    </div>
  )
}
