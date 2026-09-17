import { AlertCircle, CheckCircle, Info } from 'lucide-react'

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

const getLevelColor = (level) => {
  switch (level) {
    case 'Excellent':
      return 'bg-success-100 dark:bg-success-900 text-success-900 dark:text-success-100'
    case 'Good':
      return 'bg-primary-100 dark:bg-primary-900 text-primary-900 dark:text-primary-100'
    case 'Moderate':
      return 'bg-warning-100 dark:bg-warning-900 text-warning-900 dark:text-warning-100'
    case 'Poor':
      return 'bg-danger-100 dark:bg-danger-900 text-danger-900 dark:text-danger-100'
    default:
      return 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
  }
}

const getScoreColor = (score) => {
  if (score >= 8.75) return 'text-success-600 dark:text-success-400'
  if (score >= 7.5) return 'text-primary-600 dark:text-primary-400'
  if (score >= 5.0) return 'text-warning-600 dark:text-warning-400'
  return 'text-danger-600 dark:text-danger-400'
}

export default function DimensionValidator({ validation, overallIssues, improvementTargets }) {
  if (!validation || !validation.validation) {
    return <div className="text-gray-500 p-4">No validation data available</div>
  }

  return (
    <div className="space-y-6">
      {/* Dimensions Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b-2 border-gray-300 dark:border-gray-600">
              <th className="text-left py-2 px-3 font-semibold text-gray-900 dark:text-gray-100">Dimension</th>
              <th className="text-left py-2 px-3 font-semibold text-gray-900 dark:text-gray-100">Level</th>
              <th className="text-center py-2 px-3 font-semibold text-gray-900 dark:text-gray-100">Score</th>
              <th className="text-left py-2 px-3 font-semibold text-gray-900 dark:text-gray-100">Issues</th>
              <th className="text-left py-2 px-3 font-semibold text-gray-900 dark:text-gray-100">Recommendation</th>
            </tr>
          </thead>
          <tbody>
            {DIMENSIONS.map((dim, idx) => {
              const dimData = validation.validation[dim]
              if (!dimData) return null

              return (
                <tr
                  key={dim}
                  className={`border-b border-gray-200 dark:border-gray-700 ${idx % 2 === 0 ? 'bg-white dark:bg-gray-900' : 'bg-gray-50 dark:bg-gray-800'}`}
                >
                  <td className="py-3 px-3 font-medium text-gray-900 dark:text-gray-100 capitalize">{dim.replace(/_/g, ' ')}</td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getLevelColor(dimData.level)}`}>
                      {dimData.level}
                    </span>
                  </td>
                  <td className={`py-3 px-3 text-center font-semibold ${getScoreColor(dimData.score)}`}>
                    {dimData.score}
                  </td>
                  <td className="py-3 px-3 text-gray-700 dark:text-gray-300 text-xs max-w-xs">
                    {dimData.issues && dimData.issues.length > 0 ? dimData.issues.slice(0, 2).join(', ') : 'None'}
                  </td>
                  <td className="py-3 px-3 text-gray-700 dark:text-gray-300 text-xs max-w-xs">
                    {dimData.recommendation ? dimData.recommendation.substring(0, 60) + '...' : 'N/A'}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Overall Issues */}
      {overallIssues && overallIssues.length > 0 && (
        <div className="bg-warning-50 dark:bg-warning-900/20 border border-warning-200 dark:border-warning-700 rounded-lg p-4">
          <div className="flex gap-3 mb-2">
            <AlertCircle size={18} className="text-warning-600 dark:text-warning-400 flex-shrink-0 mt-0.5" />
            <h4 className="font-semibold text-warning-900 dark:text-warning-100">Overall Issues</h4>
          </div>
          <ul className="space-y-1 ml-7">
            {overallIssues.map((issue, idx) => (
              <li key={idx} className="text-sm text-warning-800 dark:text-warning-200">{issue}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Improvement Targets */}
      {improvementTargets && improvementTargets.length > 0 && (
        <div className="bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-700 rounded-lg p-4">
          <div className="flex gap-3 mb-2">
            <Info size={18} className="text-primary-600 dark:text-primary-400 flex-shrink-0 mt-0.5" />
            <h4 className="font-semibold text-primary-900 dark:text-primary-100">Recommended Improvements</h4>
          </div>
          <ul className="space-y-1 ml-7">
            {improvementTargets.map((target, idx) => (
              <li key={idx} className="text-sm text-primary-800 dark:text-primary-200 capitalize">{target.replace(/_/g, ' ')}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
