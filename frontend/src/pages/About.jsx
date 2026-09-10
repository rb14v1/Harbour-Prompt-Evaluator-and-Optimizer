export default function About() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="card">
        <h1 className="text-4xl font-bold mb-4">About Prompt Evaluator</h1>
        <p className="text-lg text-gray-700 dark:text-gray-300">
          Prompt Evaluator is an AI-powered tool that helps optimize prompts for better AI model performance.
          It evaluates prompts across 8 key quality dimensions and provides actionable suggestions for improvement.
        </p>
      </div>

      <div className="card">
        <h2 className="text-2xl font-bold mb-4">How It Works</h2>
        <ol className="space-y-4">
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">1</span>
            <div>
              <p className="font-semibold">Preprocessing</p>
              <p className="text-gray-600 dark:text-gray-400">Your prompt is normalized and prepared for analysis</p>
            </div>
          </li>
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">2</span>
            <div>
              <p className="font-semibold">Classification</p>
              <p className="text-gray-600 dark:text-gray-400">The prompt is categorized by task type (code, content, research, etc.)</p>
            </div>
          </li>
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">3</span>
            <div>
              <p className="font-semibold">Analysis</p>
              <p className="text-gray-600 dark:text-gray-400">Components are extracted: intent, requirements, context, constraints</p>
            </div>
          </li>
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">4</span>
            <div>
              <p className="font-semibold">Evaluation</p>
              <p className="text-gray-600 dark:text-gray-400">Scored across 8 quality dimensions on a scale of 0-10</p>
            </div>
          </li>
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">5</span>
            <div>
              <p className="font-semibold">Optimization</p>
              <p className="text-gray-600 dark:text-gray-400">If needed, prompts are automatically improved to meet quality threshold</p>
            </div>
          </li>
        </ol>
      </div>

      <div className="card">
        <h2 className="text-2xl font-bold mb-4">Evaluation Dimensions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">Clarity</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Is the request clear and unambiguous?</p>
          </div>
          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">Specificity</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Is enough detail provided to guide execution?</p>
          </div>
          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">Context</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Is relevant background information included?</p>
          </div>
          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">Completeness</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Are all necessary components present?</p>
          </div>
          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">Requirements</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Are success criteria explicit?</p>
          </div>
          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">Constraints</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Are limitations and boundaries defined?</p>
          </div>
          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">Expected Output</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Is output format/structure clear?</p>
          </div>
          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">Actionability</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Can it be executed immediately?</p>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-2xl font-bold mb-4">Technology</h2>
        <p className="text-gray-700 dark:text-gray-300 mb-4">
          Prompt Evaluator is built with modern web technologies:
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded text-center">
            <p className="font-semibold text-sm">React 18</p>
            <p className="text-xs text-gray-600 dark:text-gray-400">Frontend</p>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded text-center">
            <p className="font-semibold text-sm">Vite</p>
            <p className="text-xs text-gray-600 dark:text-gray-400">Build Tool</p>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded text-center">
            <p className="font-semibold text-sm">Django</p>
            <p className="text-xs text-gray-600 dark:text-gray-400">Backend</p>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded text-center">
            <p className="font-semibold text-sm">Azure OpenAI</p>
            <p className="text-xs text-gray-600 dark:text-gray-400">AI Engine</p>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-2xl font-bold mb-4">Get Started</h2>
        <p className="text-gray-700 dark:text-gray-300 mb-4">
          Ready to optimize your prompts? Head to the <a href="/" className="text-primary-600 hover:text-primary-700">home page</a> and
          enter your prompt to get started with instant evaluation.
        </p>
      </div>
    </div>
  )
}
