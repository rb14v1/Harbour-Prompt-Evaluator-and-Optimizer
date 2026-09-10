import { useParams, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { ArrowLeft } from 'lucide-react'
import { evaluationAPI } from '../services/api'
import EvaluationResult from '../components/EvaluationResult'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Results() {
  const { promptId } = useParams()
  const navigate = useNavigate()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const data = await evaluationAPI.getEvaluationDetail(promptId)
        setResult(data)
      } catch (err) {
        setError(err.message || 'Error loading results')
      } finally {
        setLoading(false)
      }
    }

    if (promptId) {
      fetchResult()
    }
  }, [promptId])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center">
        <p className="text-danger-600 mb-4">{error}</p>
        <button onClick={() => navigate('/')} className="btn-primary">
          Back to Home
        </button>
      </div>
    )
  }

  return (
    <div>
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-6"
      >
        <ArrowLeft size={20} />
        Back
      </button>
      {result && <EvaluationResult result={result} />}
    </div>
  )
}
