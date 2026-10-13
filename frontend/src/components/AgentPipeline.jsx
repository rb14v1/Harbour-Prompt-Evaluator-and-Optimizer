import { Check, AlertCircle, Zap } from 'lucide-react'

const AGENTS = [
  { name: 'Preprocessor', order: 1 },
  { name: 'Classifier', order: 2 },
  { name: 'Analyzer', order: 3 },
  { name: 'Validator', order: 4 },
  { name: 'Scoring', order: 5 },
  { name: 'Improver', order: 6 },
  { name: 'Report', order: 7 }
]

const getStatusIcon = (status) => {
  switch (status) {
    case 'complete':
      return <Check size={18} className="text-success-600" />
    case 'running':
      return <Zap size={18} className="text-primary-600 animate-pulse" />
    case 'pending':
      return <div className="w-4 h-4 rounded-full border-2 border-gray-400" />
    case 'failed':
    case 'skipped':
      return <AlertCircle size={18} className="text-danger-600" />
    default:
      return null
  }
}

const getStatusStyle = (status, isSelected) => {
  const baseStyle = 'p-4 rounded-lg border-2 transition-all cursor-pointer'

  if (isSelected) {
    return baseStyle + ' border-primary-600 bg-primary-50 dark:bg-primary-900/20 shadow-md'
  }

  switch (status) {
    case 'complete':
      return baseStyle + ' border-success-300 dark:border-success-700 bg-success-50 dark:bg-success-900/20 hover:border-success-400 dark:hover:border-success-600'
    case 'skipped':
      return baseStyle + ' border-warning-300 dark:border-warning-700 bg-warning-50 dark:bg-warning-900/20 opacity-75'
    case 'failed':
      return baseStyle + ' border-danger-300 dark:border-danger-700 bg-danger-50 dark:bg-danger-900/20 hover:border-danger-400 dark:hover:border-danger-600'
    default:
      return baseStyle + ' border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 hover:border-gray-400 dark:hover:border-gray-500'
  }
}

export default function AgentPipeline({ executionHistory, activeAgent, onAgentSelect, activeIteration = 0 }) {
  if (!executionHistory || !executionHistory.iterations || executionHistory.iterations.length === 0) {
    return <div className="text-gray-500 p-4">No execution history available</div>
  }

  const currentIteration = executionHistory.iterations[activeIteration]
  if (!currentIteration || !currentIteration.stages) {
    return <div className="text-gray-500 p-4">No stages available for this iteration</div>
  }

  const stages = currentIteration.stages

  const getAgentStatus = (agentKey) => {
    const stage = stages[agentKey]

    if (!stage) return 'pending'
    if (stage.status === 'skipped') return 'skipped'
    if (stage.error) return 'failed'
    if (stage.output) return 'complete'
    if (stage.input && !stage.output) return 'running'

    return 'pending'
  }

  return (
    <div className="space-y-3">
      {AGENTS.map((agent, idx) => {
        const agentKey = agent.name.toLowerCase()
        const status = getAgentStatus(agentKey)
        const isSelected = activeAgent === agentKey
        const isSkipped = status === 'skipped'

        return (
          <div key={agent.name}>
            <button
              onClick={() => !isSkipped && onAgentSelect(agentKey)}
              disabled={isSkipped}
              className={getStatusStyle(status, isSelected) + (isSkipped ? ' cursor-not-allowed' : '')}
            >
              <div className="flex items-start gap-3">
                <div className="mt-1">{getStatusIcon(status)}</div>
                <div className="flex-1 text-left">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-900 dark:text-gray-100">
                      [{agent.order}] {agent.name}
                    </span>
                    {isSkipped && (
                      <span className="text-xs bg-warning-200 dark:bg-warning-800 text-warning-900 dark:text-warning-100 px-2 py-0.5 rounded">
                        Skipped
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                    {status === 'complete' && '✓ Completed'}
                    {status === 'running' && '⟳ Running...'}
                    {status === 'pending' && '○ Pending'}
                    {status === 'failed' && '✗ Failed'}
                    {status === 'skipped' && '✗ Prompt already meets threshold'}
                  </div>
                </div>
              </div>
            </button>

            {/* Arrow between agents */}
            {idx < AGENTS.length - 1 && (
              <div className="flex justify-center py-2">
                <div className="w-0.5 h-4 bg-gradient-to-b from-gray-300 to-gray-300 dark:from-gray-600 dark:to-gray-600" />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
