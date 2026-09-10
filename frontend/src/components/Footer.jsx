export default function Footer() {
  return (
    <footer className="bg-gray-100 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-12">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="font-semibold mb-2">About</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Prompt Evaluator helps optimize your AI prompts for better results.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Quick Links</h3>
            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li><a href="#" className="hover:text-primary-600">Documentation</a></li>
              <li><a href="#" className="hover:text-primary-600">GitHub</a></li>
              <li><a href="#" className="hover:text-primary-600">Support</a></li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Status</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Backend API: <span className="text-green-600">✓ Online</span>
            </p>
          </div>
        </div>
        <div className="border-t border-gray-200 dark:border-gray-700 mt-8 pt-8 text-center text-sm text-gray-600 dark:text-gray-400">
          <p>&copy; 2026 Prompt Evaluator. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
