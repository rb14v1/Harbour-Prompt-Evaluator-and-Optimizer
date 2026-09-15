export default function TabInterface({ activeTab = 'json', onTabChange, children }) {
  const tabs = [
    { id: 'json', label: 'JSON View', icon: '{}' },
    { id: 'text', label: 'Text View', icon: '≡' }
  ]

  return (
    <div className="w-full">
      <div className="flex gap-2 border-b border-gray-300 dark:border-gray-700 mb-4">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`px-4 py-2 font-medium text-sm transition-colors ${
              activeTab === tab.id
                ? 'text-primary-600 dark:text-primary-400 border-b-2 border-primary-600 dark:border-primary-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      <div className="tab-content">
        {children}
      </div>
    </div>
  )
}
