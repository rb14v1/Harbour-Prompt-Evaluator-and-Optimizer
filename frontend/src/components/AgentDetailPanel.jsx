import { ChevronDown, ChevronRight } from 'lucide-react'
import { useState } from 'react'
import JsonDisplay from './JsonDisplay'
import DimensionValidator from './DimensionValidator'
import ScoringDisplay from './ScoringDisplay'
import TabInterface from './TabInterface'
import TableDisplay from './TableDisplay'

const AGENT_ORDER = ['preprocessor', 'classifier', 'analyzer', 'validator', 'scoring', 'improver', 'report']

const getAgentDisplayName = (agentKey) => {
  const names = {
    preprocessor: 'Preprocessor',
    classifier: 'Classifier',
    analyzer: 'Analyzer',
    validator: 'Validator',
    scoring: 'Scoring Engine',
    improver: 'Improver',
    report: 'Report'
  }
  return names[agentKey] || agentKey
}

const getPreviousAgent = (agentKey) => {
  const idx = AGENT_ORDER.indexOf(agentKey)
  return idx > 0 ? AGENT_ORDER[idx - 1] : null
}

export default function AgentDetailPanel({ stages, activeAgent, threshold = 7.0 }) {
  const [showPrevious, setShowPrevious] = useState(false)
  const [viewMode, setViewMode] = useState('json')

  if (!stages || !activeAgent) {
    return (
      <div className="bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6 text-center text-gray-500">
        Select an agent to view details
      </div>
    )
  }

  const currentStage = stages[activeAgent]
  if (!currentStage) {
    return (
      <div className="bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6 text-center text-gray-500">
        No data available for {getAgentDisplayName(activeAgent)}
      </div>
    )
  }

  const previousAgentKey = getPreviousAgent(activeAgent)
  const previousStage = previousAgentKey ? stages[previousAgentKey] : null

  // Handle skipped improver
  if (currentStage.status === 'skipped') {
    return (
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          {getAgentDisplayName(activeAgent)}
        </h3>
        <div className="bg-warning-50 dark:bg-warning-900/20 border border-warning-200 dark:border-warning-700 rounded-lg p-4">
          <p className="font-medium text-warning-900 dark:text-warning-100">Status: Skipped</p>
          <p className="text-sm text-warning-800 dark:text-warning-200 mt-2">
            {currentStage.reason || 'Prompt already meets the 7.0 quality threshold.'}
          </p>
        </div>
      </div>
    )
  }

  // Handle failed/error states
  if (currentStage.error) {
    return (
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          {getAgentDisplayName(activeAgent)}
        </h3>
        <div className="bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-700 rounded-lg p-4">
          <p className="font-medium text-danger-900 dark:text-danger-100">Status: Failed</p>
          <p className="text-sm text-danger-800 dark:text-danger-200 mt-2">
            {currentStage.error}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Previous Stage */}
      {previousStage && (
        <div className="border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setShowPrevious(!showPrevious)}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <div className="text-left">
              <h4 className="font-semibold text-gray-900 dark:text-gray-100">
                Previous Stage: {getAgentDisplayName(previousAgentKey)}
              </h4>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {showPrevious ? 'Click to collapse' : 'Click to expand'}
              </p>
            </div>
            {showPrevious ? (
              <ChevronDown size={20} className="text-gray-600 dark:text-gray-400" />
            ) : (
              <ChevronRight size={20} className="text-gray-600 dark:text-gray-400" />
            )}
          </button>

          {showPrevious && (
            <div className="px-6 pb-6 bg-gray-50 dark:bg-gray-800">
              <PreviousStageContent stage={previousStage} agentKey={previousAgentKey} />
            </div>
          )}
        </div>
      )}

      {/* Arrow divider if previous exists */}
      {previousStage && (
        <div className="flex justify-center py-2 bg-gray-50 dark:bg-gray-800">
          <div className="text-gray-400 dark:text-gray-600 font-bold">↓</div>
        </div>
      )}

      {/* Current Stage with Tabs */}
      <div className="px-6 py-6 space-y-4">
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
          Current Stage: {getAgentDisplayName(activeAgent)}
        </h3>

        <TabInterface activeTab={viewMode} onTabChange={setViewMode}>
          {viewMode === 'json' ? (
            <CurrentStageContent stage={currentStage} agentKey={activeAgent} threshold={threshold} />
          ) : (
            <div className="py-4">
              <TableDisplay data={currentStage.output || {}} />
            </div>
          )}
        </TabInterface>
      </div>
    </div>
  )
}

function PreviousStageContent({ stage, agentKey }) {
  if (agentKey === 'preprocessor') {
    return <JsonDisplay data={stage.output} title="Preprocessor Output" collapsed={true} />
  }

  if (agentKey === 'classifier') {
    return <JsonDisplay data={stage.output} title="Classification Output" collapsed={true} />
  }

  if (agentKey === 'analyzer') {
    return <JsonDisplay data={stage.output} title="Analysis Output" collapsed={true} />
  }

  if (agentKey === 'validator') {
    return (
      <DimensionValidator
        validation={stage.output}
        overallIssues={stage.output?.overall_issues}
        improvementTargets={stage.output?.improvement_targets}
      />
    )
  }

  if (agentKey === 'scoring') {
    return <ScoringDisplay scoring={stage.output} />
  }

  if (agentKey === 'improver') {
    return <JsonDisplay data={stage.output} title="Improver Output" collapsed={true} />
  }

  return <JsonDisplay data={stage.output} title={`${agentKey} Output`} collapsed={true} />
}

function CurrentStageContent({ stage, agentKey, threshold }) {
  // Preprocessor: show raw input and output
  if (agentKey === 'preprocessor') {
    return (
      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2">Original User Prompt (Input)</h4>
          <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
            {stage.input}
          </div>
        </div>
        <JsonDisplay data={stage.output} title="Processed Output" collapsed={false} />
      </div>
    )
  }

  // Classifier: show input + output
  if (agentKey === 'classifier') {
    return (
      <div className="space-y-4">
        <JsonDisplay data={stage.input} title="Input (Processed Prompt)" collapsed={true} />
        <JsonDisplay data={stage.output} title="Classification Output" collapsed={false} />
      </div>
    )
  }

  // Analyzer: show input + output
  if (agentKey === 'analyzer') {
    return (
      <div className="space-y-4">
        <JsonDisplay data={stage.input} title="Input (Classification)" collapsed={true} />
        <JsonDisplay data={stage.output} title="Analysis Output" collapsed={false} />
      </div>
    )
  }

  // Validator: special table display
  if (agentKey === 'validator') {
    return (
      <div className="space-y-4">
        <JsonDisplay data={stage.input} title="Input (Analysis)" collapsed={true} />
        <div>
          <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">Validation Dimensions</h4>
          <DimensionValidator
            validation={stage.output}
            overallIssues={stage.output?.overall_issues}
            improvementTargets={stage.output?.improvement_targets}
          />
        </div>
      </div>
    )
  }

  // Scoring: special score card display
  if (agentKey === 'scoring') {
    return (
      <div className="space-y-4">
        <JsonDisplay data={stage.input} title="Input (Validation)" collapsed={true} />
        <div>
          <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">Scoring Results</h4>
          <ScoringDisplay scoring={stage.output} threshold={threshold} />
        </div>
      </div>
    )
  }

  // Improver: show iteration info
  if (agentKey === 'improver') {
    return (
      <div className="space-y-4">
        {stage.output?.iteration && (
          <div className="bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-700 rounded-lg p-4">
            <p className="text-sm font-semibold text-primary-900 dark:text-primary-100">
              Iteration {stage.output.iteration}
            </p>
          </div>
        )}

        {stage.output?.improved_prompt && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2">Improved Prompt</h4>
            <div className="bg-success-50 dark:bg-success-900/20 border border-success-200 dark:border-success-700 p-3 rounded text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
              {stage.output.improved_prompt}
            </div>
          </div>
        )}

        {stage.output?.changes_made && stage.output.changes_made.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2">Changes Made</h4>
            <ul className="space-y-1 ml-4">
              {stage.output.changes_made.map((change, idx) => (
                <li key={idx} className="text-sm text-gray-700 dark:text-gray-300">• {change}</li>
              ))}
            </ul>
          </div>
        )}

        {stage.output?.dimensions_addressed && stage.output.dimensions_addressed.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2">Dimensions Addressed</h4>
            <div className="flex flex-wrap gap-2">
              {stage.output.dimensions_addressed.map((dim, idx) => (
                <span key={idx} className="px-2 py-1 bg-primary-100 dark:bg-primary-900 text-primary-900 dark:text-primary-100 text-xs rounded capitalize">
                  {dim.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          </div>
        )}

        {stage.output?.reasoning && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2">Reasoning</h4>
            <p className="text-sm text-gray-700 dark:text-gray-300">{stage.output.reasoning}</p>
          </div>
        )}

        {stage.output?.intent_preserved !== undefined && (
          <div className={`p-3 rounded text-sm ${
            stage.output.intent_preserved
              ? 'bg-success-50 dark:bg-success-900/20 border border-success-200 dark:border-success-700 text-success-900 dark:text-success-100'
              : 'bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-700 text-danger-900 dark:text-danger-100'
          }`}>
            Intent Preserved: {stage.output.intent_preserved ? '✓ Yes' : '✗ No'}
          </div>
        )}
      </div>
    )
  }

  // Report: comprehensive output
  if (agentKey === 'report') {
    return (
      <div className="space-y-4">
        <JsonDisplay data={stage.output} title="Complete Final Report" collapsed={false} />
      </div>
    )
  }

  // Default: just show JSON
  return <JsonDisplay data={stage.output} title={`${agentKey} Output`} collapsed={false} />
}
