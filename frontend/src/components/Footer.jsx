export default function Footer() {
  return (
    <footer className="bg-gray-100 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-12">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center text-sm text-gray-600 dark:text-gray-400">
          <p>Backend API: <span className="text-green-600">✓ Online</span></p>
        </div>
        <div className="border-t border-gray-200 dark:border-gray-700 mt-8 pt-8 text-center text-sm text-gray-600 dark:text-gray-400">
          <p>&copy; 2026 Prompt Evaluator. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
