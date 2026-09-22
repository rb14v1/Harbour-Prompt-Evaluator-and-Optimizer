import { useState } from 'react'
import PromptForm from '../components/PromptForm'
import SimpleResults from '../components/SimpleResults'

export default function Home() {
  const [result, setResult] = useState(null)

  const handleSuccess = (data) => {
    setResult(data)
  }

  if (result) {
    return (
      <div>
        <SimpleResults result={result} />
        <div className="mt-8 flex gap-4 justify-center">
          <button
            onClick={() => setResult(null)}
            className="btn-primary"
          >
            Evaluate Another Prompt
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

      {/* How It Works */}
      <section className="bg-gray-50 dark:bg-gray-800 rounded-lg p-8">
        <h2 className="text-3xl font-bold mb-8 text-center">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
            <p className="font-semibold">Download Report</p>
          </div>
        </div>
      </section>
    </div>
  )
}
