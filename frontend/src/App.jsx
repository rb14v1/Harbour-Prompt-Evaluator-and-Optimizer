import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Moon, Sun } from 'lucide-react'
import Header from './components/Header'
import Footer from './components/Footer'
import Home from './pages/Home'
import Results from './pages/Results'
import History from './pages/History'
import About from './pages/About'
import ComparePrompts from './pages/ComparePrompts'
import './App.css'

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode')
    return saved ? JSON.parse(saved) : false
  })

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
  }

  return (
    <BrowserRouter>
      <div className={`flex flex-col min-h-screen ${darkMode ? 'dark' : ''} bg-white dark:bg-gray-900 text-gray-900 dark:text-white transition-colors duration-200`}>
        <Header darkMode={darkMode} toggleDarkMode={toggleDarkMode} />

        <main className="flex-grow container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/results/:promptId" element={<Results />} />
            <Route path="/history" element={<History />} />
            <Route path="/about" element={<About />} />
            <Route path="/compare" element={<ComparePrompts />} />
          </Routes>
        </main>

        <Footer />
      </div>
    </BrowserRouter>
  )
}

export default App
