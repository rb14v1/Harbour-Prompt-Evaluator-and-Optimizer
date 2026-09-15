import { ChevronDown, ChevronRight } from 'lucide-react'
import { useState } from 'react'

function formatValue(value) {
  if (value === null || value === undefined) return 'N/A'
  if (typeof value === 'boolean') return value ? 'Yes' : 'No'
  if (typeof value === 'object') {
    if (Array.isArray(value)) {
      return value.length > 0 ? value.join(', ') : '[]'
    }
    return '[Object]'
  }
  if (typeof value === 'string') {
    return value.length > 100 ? value.substring(0, 100) + '...' : value
  }
  return String(value)
}

function TableRow({ field, value, isNested = false }) {
  const [expanded, setExpanded] = useState(false)
  const isObject = typeof value === 'object' && value !== null

  return (
    <div className="border-b border-gray-200 dark:border-gray-700">
      <div className={`flex items-start gap-3 py-3 px-4 ${isNested ? 'pl-8 bg-gray-50 dark:bg-gray-800/50' : 'hover:bg-gray-50 dark:hover:bg-gray-800/30'}`}>
        <div className="flex-shrink-0 w-6">
          {isObject && Array.isArray(value) && value.length > 0 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="p-0 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
            >
              {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </button>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-medium text-gray-700 dark:text-gray-300 text-sm break-words">
            {field.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').toUpperCase().trim()}
          </div>
          <div className="text-gray-600 dark:text-gray-400 text-sm mt-1 break-words max-w-xl">
            {formatValue(value)}
          </div>
        </div>
      </div>

      {expanded && isObject && Array.isArray(value) && value.length > 0 && (
        <div className="bg-gray-50 dark:bg-gray-800/30 pl-8">
          {value.map((item, idx) => (
            <div key={idx} className="py-2 px-4 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
              <div className="text-xs text-gray-500 dark:text-gray-500 mb-1">Item {idx + 1}</div>
              <div className="text-sm text-gray-700 dark:text-gray-300 break-words">
                {typeof item === 'object' ? JSON.stringify(item) : String(item)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function TableDisplay({ data = {} }) {
  if (!data || typeof data !== 'object') {
    return (
      <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded text-gray-600 dark:text-gray-400">
        <p>No data to display</p>
      </div>
    )
  }

  const entries = Object.entries(data)

  if (entries.length === 0) {
    return (
      <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded text-gray-600 dark:text-gray-400">
        <p>Empty object</p>
      </div>
    )
  }

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden bg-white dark:bg-gray-900">
      <div className="bg-gray-100 dark:bg-gray-800 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-sm">Data Summary</h3>
      </div>

      <div className="divide-y divide-gray-200 dark:divide-gray-700 max-h-[500px] overflow-y-auto">
        {entries.map(([key, value]) => (
          <TableRow key={key} field={key} value={value} />
        ))}
      </div>
    </div>
  )
}
