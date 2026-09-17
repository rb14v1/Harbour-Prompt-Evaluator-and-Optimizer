export default function About() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="card bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-900/10">
        <h1 className="text-4xl font-bold mb-4 text-gray-900 dark:text-white">Prompt Evaluator & Optimizer</h1>
        <p className="text-lg text-gray-700 dark:text-gray-300 mb-4">
          An intelligent, multi-agent system designed to evaluate and optimize AI prompts systematically.
        </p>
        <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div className="text-center">
            <p className="text-3xl font-bold text-primary-600">7</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">AI Agents</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-primary-600">8</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Quality Dimensions</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-primary-600">3</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Max Iterations</p>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-2xl font-bold mb-4">Project Overview</h2>
        <div className="space-y-4 text-gray-700 dark:text-gray-300">
          <p>
            <strong>Mission:</strong> Provide systematic, AI-driven evaluation and improvement of prompts to maximize their effectiveness
            when used with large language models.
          </p>
          <p>
            <strong>Use Cases:</strong>
          </p>
          <ul className="list-disc list-inside space-y-2 ml-2">
            <li>Developers optimizing prompts for production LLM applications</li>
            <li>Content creators improving prompt clarity for AI assistants</li>
            <li>Researchers analyzing prompt quality patterns</li>
            <li>Teams standardizing prompt writing guidelines</li>
            <li>Quality assurance of AI-generated outputs</li>
          </ul>
          <p>
            <strong>Key Feature:</strong> Automated prompt rewriting and iterative improvement until quality threshold (9.8/10) is reached,
            with comprehensive analysis across 8 quality dimensions.
          </p>
        </div>
      </div>

      <div className="card">
        <h2 className="text-2xl font-bold mb-4">Agent Pipeline Architecture</h2>
        <p className="text-gray-700 dark:text-gray-300 mb-6">
          The system uses a 7-agent orchestration pipeline, each responsible for a specific stage of prompt evaluation and optimization:
        </p>
        <ol className="space-y-4">
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">1</span>
            <div>
              <p className="font-semibold">Preprocessor Agent</p>
              <p className="text-gray-600 dark:text-gray-400">Normalizes text, preserves original, extracts metadata (ID, length, timestamp)</p>
            </div>
          </li>
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">2</span>
            <div>
              <p className="font-semibold">Classifier Agent</p>
              <p className="text-gray-600 dark:text-gray-400">Categorizes prompt by task type (9 categories), assesses complexity, generates confidence score</p>
            </div>
          </li>
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">3</span>
            <div>
              <p className="font-semibold">Analyzer Agent</p>
              <p className="text-gray-600 dark:text-gray-400">Decomposes prompt into: intent, requirements, context, constraints, expected output, missing information</p>
            </div>
          </li>
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">4</span>
            <div>
              <p className="font-semibold">Validator Agent</p>
              <p className="text-gray-600 dark:text-gray-400">Evaluates across 8 dimensions, rates quality levels (Poor/Moderate/Good/Excellent), provides evidence and improvement targets</p>
            </div>
          </li>
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">5</span>
            <div>
              <p className="font-semibold">Scoring Engine</p>
              <p className="text-gray-600 dark:text-gray-400">Converts qualitative ratings to numerical scores (2.5-10.0), calculates overall score, identifies low-scoring dimensions</p>
            </div>
          </li>
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-warning-600 text-white rounded-full flex items-center justify-center font-bold">6A</span>
            <div>
              <p className="font-semibold">Improver Agent (if score &lt; 9.8)</p>
              <p className="text-gray-600 dark:text-gray-400">Rewrites prompt to address weaknesses, preserves intent, focuses on low-scoring dimensions. Loops up to 3 times.</p>
            </div>
          </li>
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-success-600 text-white rounded-full flex items-center justify-center font-bold">7</span>
            <div>
              <p className="font-semibold">Report Agent (if score ≥ 9.8 or max iterations reached)</p>
              <p className="text-gray-600 dark:text-gray-400">Generates comprehensive report with original/improved prompts, full evaluation history, scores, and recommendations</p>
            </div>
          </li>
        </ol>
      </div>

      <div className="card">
        <h2 className="text-2xl font-bold mb-4">How It Works: Flow Diagram</h2>
        <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg font-mono text-xs text-gray-700 dark:text-gray-300 overflow-x-auto">
          <pre>{`User Prompt
    ↓
┌─ Preprocessor (normalize, structure)
    ↓
┌─ Classifier (categorize, assess complexity)
    ↓
┌─ Analyzer (decompose into components)
    ↓
┌─ Validator (evaluate 8 dimensions)
    ↓
┌─ Scoring Engine (calculate scores)
    ↓
    ├─ Score ≥ 9.8? ──→ Report Agent ──→ Output Result
    │
    └─ Score < 9.8? ──→ Improver Agent (rewrite prompt)
            ↓
        Re-validate ──→ Score ≥ 9.8?
        (Loop up to 3x)        │
                              ├─ Yes ──→ Report Agent ──→ Output
                              └─ No ──→ Report (Manual Review)`}</pre>
        </div>
      </div>

      <div className="card">
        <h2 className="text-2xl font-bold mb-6">8 Quality Evaluation Dimensions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded">
            <p className="font-semibold text-blue-900 dark:text-blue-100">1. Clarity</p>
            <p className="text-sm text-blue-800 dark:text-blue-200">Is the request unambiguous and easy to understand? Are technical terms defined?</p>
          </div>
          <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700 rounded">
            <p className="font-semibold text-purple-900 dark:text-purple-100">2. Specificity</p>
            <p className="text-sm text-purple-800 dark:text-purple-200">Is enough detail provided? Are examples or specific requirements mentioned?</p>
          </div>
          <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded">
            <p className="font-semibold text-green-900 dark:text-green-100">3. Context</p>
            <p className="text-sm text-green-800 dark:text-green-200">Is relevant background information included? Is domain knowledge provided?</p>
          </div>
          <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded">
            <p className="font-semibold text-yellow-900 dark:text-yellow-100">4. Completeness</p>
            <p className="text-sm text-yellow-800 dark:text-yellow-200">Are all necessary information components present? Nothing missing?</p>
          </div>
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded">
            <p className="font-semibold text-red-900 dark:text-red-100">5. Requirements</p>
            <p className="text-sm text-red-800 dark:text-red-200">Are success criteria and expectations explicit? Are goals clearly stated?</p>
          </div>
          <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-700 rounded">
            <p className="font-semibold text-indigo-900 dark:text-indigo-100">6. Constraints</p>
            <p className="text-sm text-indigo-800 dark:text-indigo-200">Are limitations and boundaries defined? Budget, time, technical constraints?</p>
          </div>
          <div className="p-4 bg-pink-50 dark:bg-pink-900/20 border border-pink-200 dark:border-pink-700 rounded">
            <p className="font-semibold text-pink-900 dark:text-pink-100">7. Expected Output</p>
            <p className="text-sm text-pink-800 dark:text-pink-200">Is output format clear? Format, structure, length, style specified?</p>
          </div>
          <div className="p-4 bg-cyan-50 dark:bg-cyan-900/20 border border-cyan-200 dark:border-cyan-700 rounded">
            <p className="font-semibold text-cyan-900 dark:text-cyan-100">8. Actionability</p>
            <p className="text-sm text-cyan-800 dark:text-cyan-200">Can it be executed immediately? All required info available to start?</p>
          </div>
        </div>

        <div className="mt-6 p-4 bg-gray-100 dark:bg-gray-800 rounded">
          <p className="font-semibold mb-2">Scoring Scale:</p>
          <div className="grid grid-cols-4 gap-3 text-sm">
            <div>
              <p className="font-bold text-red-600">2.5/10</p>
              <p className="text-gray-600 dark:text-gray-400">Poor</p>
            </div>
            <div>
              <p className="font-bold text-yellow-600">5.0/10</p>
              <p className="text-gray-600 dark:text-gray-400">Moderate</p>
            </div>
            <div>
              <p className="font-bold text-green-600">7.5/10</p>
              <p className="text-gray-600 dark:text-gray-400">Good</p>
            </div>
            <div>
              <p className="font-bold text-emerald-600">10.0/10</p>
              <p className="text-gray-600 dark:text-gray-400">Excellent</p>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-2xl font-bold mb-4">Prompt Task Categories (9 Types)</h2>
        <p className="text-gray-700 dark:text-gray-300 mb-4">
          The system classifies prompts into one of 9 task categories:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">1. Create Content</p>
            <p className="text-xs text-gray-600 dark:text-gray-400">Generate text, documents, articles</p>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">2. Create Code</p>
            <p className="text-xs text-gray-600 dark:text-gray-400">Write or refactor source code</p>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">3. Research</p>
            <p className="text-xs text-gray-600 dark:text-gray-400">Gather and brief synthesis</p>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">4. Deep Research</p>
            <p className="text-xs text-gray-600 dark:text-gray-400">Extended investigation, detailed synthesis</p>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">5. Plan & Organize</p>
            <p className="text-xs text-gray-600 dark:text-gray-400">Structure projects, create outlines</p>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">6. Ideate</p>
            <p className="text-xs text-gray-600 dark:text-gray-400">Brainstorm concepts, generate ideas</p>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">7. Summarize</p>
            <p className="text-xs text-gray-600 dark:text-gray-400">Condense existing information</p>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">8. Explain</p>
            <p className="text-xs text-gray-600 dark:text-gray-400">Teach concepts, clarify topics</p>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-semibold">9. Optimize</p>
            <p className="text-xs text-gray-600 dark:text-gray-400">Improve performance, efficiency</p>
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
