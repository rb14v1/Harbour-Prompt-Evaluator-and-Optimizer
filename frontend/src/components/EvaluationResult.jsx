import { Check, AlertCircle, RefreshCw } from 'lucide-react'
import ScoreCard from './ScoreCard'
import DimensionChart from './DimensionChart'

export default function EvaluationResult({ result }) {
  if (!result) return null

  const statusIcon = result.status === 'Ready' ? <Check className="text-success-500" /> : <AlertCircle className="text-warning-500" />
  const statusColor = result.status === 'Ready' ? 'bg-success-100 dark:bg-success-900 text-success-800 dark:text-success-200' : 'bg-warning-100 dark:bg-warning-900 text-warning-800 dark:text-warning-200'

  return (
    <div className="space-y-6">
      {/* Header with Status */}
      <div className="card">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h2 className="text-2xl font-bold mb-2">Evaluation Results</h2>
            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${statusColor}`}>
              {statusIcon}
              {result.status}
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600 dark:text-gray-400">Final Score</p>
            <p className="text-4xl font-bold text-primary-600">{result.final_score.toFixed(2)}</p>
          </div>
        </div>

        <p className="text-gray-700 dark:text-gray-300 mb-4">{result.summary}</p>

        {result.improvements_made > 0 && (
          <div className="bg-primary-50 dark:bg-primary-900 p-3 rounded-lg flex items-start gap-2">
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
        <div className="card">
          <h3 className="font-bold mb-2">Original Prompt</h3>
          <p className="text-sm text-gray-700 dark:text-gray-300 p-3 bg-gray-50 dark:bg-gray-700 rounded">
            {result.original_prompt}
          </p>
        </div>

        {result.final_prompt !== result.original_prompt && (
          <div className="card border-2 border-success-500">
            <h3 className="font-bold mb-2 flex items-center gap-2">
              <Check size={18} className="text-success-500" />
              Improved Prompt
            </h3>
            <p className="text-sm text-gray-700 dark:text-gray-300 p-3 bg-success-50 dark:bg-success-900 rounded">
              {result.final_prompt}
            </p>
          </div>
        )}
      </div>

      {/* Scores */}
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
      <DimensionChart scores={result.final_evaluation.dimension_scores} />

      {/* Improvement History */}
      {result.improvement_history && result.improvement_history.length > 0 && (
        <div className="card">
          <h3 className="text-xl font-bold mb-4">Improvement History</h3>
          <div className="space-y-4">
            {result.improvement_history.map((improvement, idx) => (
              <div key={idx} className="border-l-4 border-primary-600 pl-4 py-2">
                <p className="font-semibold text-sm">Iteration {improvement.iteration}</p>
                <ul className="text-sm text-gray-600 dark:text-gray-400 mt-1 space-y-1">
                  {improvement.changes_made.map((change, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-primary-600 mt-0.5">•</span>
                      <span>{change}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Classification */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <p className="text-sm text-gray-600 dark:text-gray-400">Task Type</p>
          <p className="font-semibold text-lg">{result.classification.task_type}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600 dark:text-gray-400">Complexity</p>
          <p className="font-semibold text-lg">{result.classification.complexity}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600 dark:text-gray-400">Confidence</p>
          <p className="font-semibold text-lg">{(result.classification.confidence * 100).toFixed(0)}%</p>
        </div>
      </div>
    </div>
  )
}
