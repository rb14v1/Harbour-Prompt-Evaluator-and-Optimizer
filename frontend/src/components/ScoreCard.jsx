export default function ScoreCard({ score, maxScore = 10, label, subtitle }) {
  const percentage = (score / maxScore) * 100
  let colorClass = 'poor'

  if (score >= 8.5) colorClass = 'excellent'
  else if (score >= 7) colorClass = 'good'
  else if (score >= 5) colorClass = 'moderate'
  else colorClass = 'poor'

  return (
    <div className="flex flex-col items-center p-6 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <div className={`score-badge ${colorClass}`}>
        {score.toFixed(1)}
      </div>
      <p className="mt-3 font-semibold text-center">{label}</p>
      {subtitle && <p className="text-sm text-gray-600 dark:text-gray-400 text-center">{subtitle}</p>}
      <div className="w-full mt-3 bg-gray-300 dark:bg-gray-600 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${
            colorClass === 'excellent' ? 'bg-success-500' :
            colorClass === 'good' ? 'bg-primary-500' :
            colorClass === 'moderate' ? 'bg-warning-500' :
            'bg-danger-500'
          }`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  )
}
