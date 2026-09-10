import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Zap, BarChart3, Repeat2, Shield } from 'lucide-react'
import PromptForm from '../components/PromptForm'
import EvaluationResult from '../components/EvaluationResult'

export default function Home() {
  const [result, setResult] = useState(null)
  const navigate = useNavigate()

  const handleSuccess = (data) => {
    setResult(data)
  }

  if (result) {
    return (
      <div>
        <EvaluationResult result={result} />
        <div className="mt-8 flex gap-4 justify-center">
          <button
            onClick={() => setResult(null)}
            className="btn-primary"
          >
            Evaluate Another Prompt
          </button>
          <button
            onClick={() => navigate('/history')}
            className="btn-secondary"
          >
            View History
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-12">
        <h1 className="text-5xl md:text-6xl font-bold mb-4 gradient-text">
          Optimize Your Prompts
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-6">
          Get AI-powered evaluation and improvement suggestions for your prompts.
          Evaluated across 8 quality dimensions.
        </p>
      </section>

      {/* Prompt Form */}
      <PromptForm onSuccess={handleSuccess} />

      {/* Features Grid */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card text-center">
          <Zap className="w-12 h-12 mx-auto text-primary-600 mb-3" />
          <h3 className="font-bold mb-2">Instant Evaluation</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Get results in seconds with our AI evaluation engine
          </p>
        </div>

        <div className="card text-center">
          <BarChart3 className="w-12 h-12 mx-auto text-success-600 mb-3" />
          <h3 className="font-bold mb-2">8 Dimensions</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Evaluated on clarity, specificity, completeness, and more
          </p>
        </div>

        <div className="card text-center">
          <Repeat2 className="w-12 h-12 mx-auto text-warning-600 mb-3" />
          <h3 className="font-bold mb-2">Auto Improvement</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Automatic prompt rewriting to reach quality threshold
          </p>
        </div>

        <div className="card text-center">
          <Shield className="w-12 h-12 mx-auto text-danger-600 mb-3" />
          <h3 className="font-bold mb-2">Privacy First</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Your prompts are evaluated securely and privately
          </p>
        </div>
      </section>

      {/* How It Works */}
      <section className="bg-gray-50 dark:bg-gray-800 rounded-lg p-8">
        <h2 className="text-3xl font-bold mb-8 text-center">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="w-10 h-10 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold mx-auto mb-2">
              1
            </div>
            <p className="font-semibold">Enter Your Prompt</p>
          </div>
          <div className="text-center">
            <div className="w-10 h-10 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold mx-auto mb-2">
              2
            </div>
            <p className="font-semibold">Get Evaluated</p>
          </div>
          <div className="text-center">
            <div className="w-10 h-10 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold mx-auto mb-2">
              3
            </div>
            <p className="font-semibold">View Results</p>
          </div>
          <div className="text-center">
            <div className="w-10 h-10 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold mx-auto mb-2">
              4
            </div>
            <p className="font-semibold">Track History</p>
          </div>
        </div>
      </section>
    </div>
  )
}
