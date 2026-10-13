export default function IterationTabs({ iterations, activeIteration, onIterationChange }) {
  if (!iterations || iterations.length === 0) {
    return null
  }

  return (
    <div className="flex gap-2 p-4 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
      {iterations.map((iter, idx) => {
        const score = iter.stages?.scoring?.output?.overall_score ?? 'N/A'
        const isActive = activeIteration === idx

        return (
          <button
            key={idx}
            onClick={() => onIterationChange(idx)}
            className={`px-4 py-2 rounded font-medium text-sm whitespace-nowrap transition-colors ${
              isActive
                ? 'bg-primary-600 text-white shadow-md'
                : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-600 border border-gray-200 dark:border-gray-600'
            }`}
          >
            <div>Iteration {idx}</div>
            <div className="text-xs opacity-75">
              Score: {typeof score === 'number' ? score.toFixed(2) : score}
            </div>
          </button>
        )
      })}
    </div>
  )
}
