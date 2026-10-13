import { TrendingUp } from 'lucide-react'

const DIMENSIONS = [
  'clarity',
  'specificity',
  'context',
  'completeness',
  'requirements',
  'constraints',
  'expected_output',
  'actionability'
]

const getScoreColor = (score, threshold = 9.5) => {
  if (score >= threshold) return 'from-success-500 to-success-600'
  if (score >= 5.0) return 'from-warning-500 to-warning-600'
  return 'from-danger-500 to-danger-600'
}

const getStatusColor = (status) => {
  switch (status) {
    case 'Ready':
      return 'bg-success-100 dark:bg-success-900 text-success-900 dark:text-success-100'
    case 'Needs Improvement':
      return 'bg-warning-100 dark:bg-warning-900 text-warning-900 dark:text-warning-100'
    default:
      return 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
  }
}

export default function ScoringDisplay({ scoring, threshold = 9.5 }) {
  if (!scoring) return <div className="text-gray-500 p-4">No scoring data available</div>

  const overallScore = scoring.overall_score || 0
  const status = overallScore >= threshold ? 'Ready' : 'Needs Improvement'
  const scorePercent = Math.min((overallScore / 10) * 100, 100)

  return (
    <div className="space-y-6">
      {/* Main Score Card */}
      <div className={`bg-gradient-to-br ${getScoreColor(overallScore, threshold)} text-white rounded-lg p-6 shadow-md`}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm opacity-90 mb-1">Overall Score</p>
            <p className="text-4xl font-bold">{overallScore.toFixed(2)}</p>
            <p className="text-sm opacity-75 mt-1">/ 10.0</p>
          </div>
          <div>
            <p className="text-sm opacity-90 mb-1">Threshold</p>
            <p className="text-3xl font-bold">{threshold.toFixed(1)}</p>
            <p className="text-sm opacity-75 mt-1">Passing score</p>
          </div>
          <div>
            <p className="text-sm opacity-90 mb-1">Status</p>
            <p className="text-lg font-semibold">{status}</p>
            <div className="text-sm opacity-75 mt-2">
              {overallScore >= threshold ? '✓ Meets requirements' : '○ Needs work'}
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-6">
          <div className="bg-white/20 rounded-full h-2 overflow-hidden">
            <div
              className="bg-white h-full rounded-full transition-all duration-300"
              style={{ width: `${scorePercent}%` }}
            />
          </div>
        </div>
      </div>

      {/* Dimension Breakdown */}
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
          <TrendingUp size={18} />
          Dimension Scores
        </h4>

        <div className="space-y-3">
          {DIMENSIONS.map((dim) => {
            const score = scoring.dimension_scores?.[dim] || 0
            const percent = Math.min((score / 10) * 100, 100)
            const isLowScoring = scoring.low_scoring_dimensions?.includes(dim)
            const isHighScoring = scoring.high_performing_dimensions?.includes(dim)

            return (
              <div key={dim}>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
                    {dim.replace(/_/g, ' ')}
                    {isLowScoring && <span className="ml-2 text-xs bg-danger-100 dark:bg-danger-900 text-danger-900 dark:text-danger-100 px-2 py-0.5 rounded">Low</span>}
                    {isHighScoring && <span className="ml-2 text-xs bg-success-100 dark:bg-success-900 text-success-900 dark:text-success-100 px-2 py-0.5 rounded">High</span>}
                  </label>
                  <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">{score.toFixed(1)}</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-300 ${
                      score >= threshold
                        ? 'bg-success-500'
                        : score >= 5.0
                        ? 'bg-warning-500'
                        : 'bg-danger-500'
                    }`}
                    style={{ width: `${percent}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {scoring.low_scoring_dimensions && scoring.low_scoring_dimensions.length > 0 && (
          <div className="bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-700 rounded-lg p-4">
            <p className="text-sm font-semibold text-danger-900 dark:text-danger-100 mb-2">
              Low-Scoring Dimensions ({scoring.low_scoring_dimensions.length})
            </p>
            <ul className="space-y-1">
              {scoring.low_scoring_dimensions.map((dim, idx) => (
                <li key={idx} className="text-sm text-danger-800 dark:text-danger-200 capitalize">
                  • {dim.replace(/_/g, ' ')}
                </li>
              ))}
            </ul>
          </div>
        )}

        {scoring.high_performing_dimensions && scoring.high_performing_dimensions.length > 0 && (
          <div className="bg-success-50 dark:bg-success-900/20 border border-success-200 dark:border-success-700 rounded-lg p-4">
            <p className="text-sm font-semibold text-success-900 dark:text-success-100 mb-2">
              High-Performing Dimensions ({scoring.high_performing_dimensions.length})
            </p>
            <ul className="space-y-1">
              {scoring.high_performing_dimensions.map((dim, idx) => (
                <li key={idx} className="text-sm text-success-800 dark:text-success-200 capitalize">
                  ✓ {dim.replace(/_/g, ' ')}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
