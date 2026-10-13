import { ChevronDown, ChevronRight, Copy, Check } from 'lucide-react'
import { useState } from 'react'

export default function JsonDisplay({ data, title, collapsed = false }) {
  const [isExpanded, setIsExpanded] = useState(!collapsed)
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="flex items-center gap-3 flex-1">
          {isExpanded ? <ChevronDown size={18} className="text-gray-600 dark:text-gray-400" /> : <ChevronRight size={18} className="text-gray-600 dark:text-gray-400" />}
          <h4 className="font-medium text-gray-900 dark:text-gray-100">{title}</h4>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation()
            handleCopy()
          }}
          className="p-2 hover:bg-gray-300 dark:hover:bg-gray-600 rounded transition-colors"
          title="Copy JSON"
        >
          {copied ? <Check size={16} className="text-success-500" /> : <Copy size={16} className="text-gray-600 dark:text-gray-400" />}
        </button>
      </div>

      {isExpanded && (
        <pre className="p-4 text-sm font-mono text-gray-800 dark:text-gray-200 overflow-x-auto max-h-96 overflow-y-auto">
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  )
}
