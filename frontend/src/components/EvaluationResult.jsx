import { Check, AlertCircle, RefreshCw } from 'lucide-react'
import { useState } from 'react'
import ScoreCard from './ScoreCard'
import DimensionChart from './DimensionChart'
import AgentPipeline from './AgentPipeline'
import AgentDetailPanel from './AgentDetailPanel'
import IterationTabs from './IterationTabs'

const THRESHOLD = 7.0

export default function EvaluationResult({ result, isLoading = false }) {
  const [activeAgent, setActiveAgent] = useState('preprocessor')
  const [activeIteration, setActiveIteration] = useState(0)

  if (!result) return null

  // Extract execution history
  const executionHistory = result.execution_history
  if (!executionHistory || !executionHistory.iterations) {
    return <div className="text-gray-500 p-4">No execution history available</div>
  }

  const statusIcon = result.status === 'Ready' ? <Check className="text-success-500" /> : <AlertCircle className="text-warning-500" />
  const statusColor = result.status === 'Ready' ? 'bg-success-100 dark:bg-success-900 text-success-800 dark:text-success-200' : 'bg-warning-100 dark:bg-warning-900 text-warning-800 dark:text-warning-200'

  // Get current iteration stages
  const currentIteration = executionHistory.iterations[activeIteration]
  const stages = currentIteration?.stages || {}

  return (
    <div className="space-y-6">
      {/* Header with Status & Score */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg p-6 shadow-md">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-2xl font-bold mb-2">Evaluation Pipeline Inspector</h2>
            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${statusColor}`}>
              {statusIcon}
              {result.status}
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm opacity-90 mb-1">Final Score</p>
            <p className="text-4xl font-bold">{result.final_score ? result.final_score.toFixed(2) : 'N/A'}/10</p>
            <p className="text-xs opacity-75 mt-1">Threshold: {THRESHOLD}</p>
          </div>
        </div>

        <div className="mt-4 flex gap-4 text-sm">
          <div>
            <p className="opacity-75">Iterations</p>
            <p className="font-semibold">{result.iterations_required}/{3}</p>
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

      {/* Agent Pipeline Inspector Layout */}
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

      {/* Original vs Final Prompt */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-3">Original Prompt</h3>
          <p className="text-sm text-gray-700 dark:text-gray-300 p-3 bg-gray-50 dark:bg-gray-800 rounded">
            {result.original_prompt}
          </p>
        </div>

        {result.final_prompt !== result.original_prompt && (
          <div className="bg-white dark:bg-gray-900 rounded-lg border border-success-500 border-2 p-6">
            <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
              <Check size={18} className="text-success-500" />
              Improved Prompt
            </h3>
            <p className="text-sm text-gray-700 dark:text-gray-300 p-3 bg-success-50 dark:bg-success-900/20 rounded">
              {result.final_prompt}
            </p>
          </div>
        )}
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
        <DimensionChart scores={result.final_evaluation.dimension_scores} />
      </div>
    </div>
  )
}
