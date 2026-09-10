import { useState, useEffect } from 'react'
import { evaluationAPI } from '../services/api'
import { Link } from 'react-router-dom'
import LoadingSpinner from '../components/LoadingSpinner'
import { Eye } from 'lucide-react'

export default function History() {
  const [history, setHistory] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const historyData = await evaluationAPI.getHistory()
        const statsData = await evaluationAPI.getStats()
        setHistory(historyData)
        setStats(statsData)
      } catch (err) {
        setError(err.message || 'Error loading history')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="card text-center">
            <p className="text-3xl font-bold text-primary-600">{stats.total_prompts}</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Total Prompts</p>
          </div>
          <div className="card text-center">
            <p className="text-3xl font-bold text-success-600">{stats.prompts_ready}</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Ready</p>
          </div>
          <div className="card text-center">
            <p className="text-3xl font-bold text-warning-600">{stats.prompts_needing_review}</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Need Review</p>
          </div>
          <div className="card text-center">
            <p className="text-3xl font-bold text-primary-600">{stats.average_score?.toFixed(1) || 0}</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Avg Score</p>
          </div>
        </div>
      )}

      {/* History List */}
      <div className="card">
        <h2 className="text-2xl font-bold mb-4">Evaluation History</h2>

        {error && (
          <div className="p-3 bg-danger-100 dark:bg-danger-900 text-danger-700 dark:text-danger-200 rounded mb-4">
            {error}
          </div>
        )}

        {history.length === 0 ? (
          <p className="text-gray-600 dark:text-gray-400 text-center py-8">
            No evaluations yet. <Link to="/" className="text-primary-600 hover:text-primary-700">Start evaluating</Link>
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="table-cell text-left">Prompt</th>
                  <th className="table-cell text-center hidden md:table-cell">Score</th>
                  <th className="table-cell text-center">Status</th>
                  <th className="table-cell text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => (
                  <tr key={item.id} className="table-row">
                    <td className="table-cell max-w-xs">
                      <p className="truncate">{item.original_prompt}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(item.created_at).toLocaleDateString()}
                      </p>
                    </td>
                    <td className="table-cell text-center hidden md:table-cell">
                      <span className="font-semibold text-primary-600">{item.final_score?.toFixed(1) || 'N/A'}</span>
                    </td>
                    <td className="table-cell text-center">
                      <span className={`text-xs font-semibold px-2 py-1 rounded ${
                        item.status === 'ready' ? 'bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-200' : 'bg-warning-100 text-warning-800 dark:bg-warning-900 dark:text-warning-200'
                      }`}>
                        {item.status || 'N/A'}
                      </span>
                    </td>
                    <td className="table-cell text-center">
                      <Link
                        to={`/results/${item.id}`}
                        className="inline-flex items-center gap-1 text-primary-600 hover:text-primary-700"
                      >
                        <Eye size={16} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
