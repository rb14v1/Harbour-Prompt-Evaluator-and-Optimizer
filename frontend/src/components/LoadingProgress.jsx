import { CheckCircle, Loader2, Circle } from 'lucide-react'
import { useEffect, useState } from 'react'

const AGENTS = [
  { name: 'Preprocessor', estimatedTime: 1 },
  { name: 'Classifier', estimatedTime: 2 },
  { name: 'Analyzer', estimatedTime: 3 },
  { name: 'Validator', estimatedTime: 2 },
  { name: 'Scoring', estimatedTime: 1 },
  { name: 'Improver', estimatedTime: 3 },
  { name: 'Report', estimatedTime: 1 }
]

export default function LoadingProgress({ onComplete = () => {} }) {
  const [elapsed, setElapsed] = useState(0)
  const [completed, setCompleted] = useState([])

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsed(prev => {
        const newElapsed = prev + 0.1
        // Simulate agent completion times
        const totalTime = AGENTS.reduce((sum, a) => sum + a.estimatedTime, 0)

        const newCompleted = AGENTS.filter(agent => {
          let time = 0
          for (let a of AGENTS) {
            if (a.name === agent.name) break
            time += a.estimatedTime
          }
          return newElapsed >= time
        }).map(a => a.name)

        setCompleted(newCompleted)

        // Call onComplete if all agents are done
        if (newCompleted.length === AGENTS.length) {
          onComplete()
        }

        return newElapsed
      })
    }, 100)

    return () => clearInterval(timer)
  }, [onComplete])

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-lg max-w-md mx-auto">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Evaluating Prompt...</h3>

      <div className="space-y-3">
        {AGENTS.map((agent, idx) => {
          const isCompleted = completed.includes(agent.name)
          const isRunning = completed.length === idx + 1

          return (
            <div key={agent.name} className="flex items-center gap-3">
              {isCompleted ? (
                <CheckCircle size={20} className="text-success-500 flex-shrink-0" />
              ) : isRunning ? (
                <Loader2 size={20} className="text-primary-500 animate-spin flex-shrink-0" />
              ) : (
                <Circle size={20} className="text-gray-300 dark:text-gray-600 flex-shrink-0" />
              )}
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{agent.name}</p>
                {isRunning && (
                  <p className="text-xs text-gray-500 dark:text-gray-400">Running...</p>
                )}
              </div>
            </div>
          )
        })}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {completed.length} of {AGENTS.length} stages completed
        </p>
        <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
          <div
            className="bg-primary-600 h-full rounded-full transition-all duration-300"
            style={{ width: `${(completed.length / AGENTS.length) * 100}%` }}
          />
        </div>
      </div>
    </div>
  )
}
