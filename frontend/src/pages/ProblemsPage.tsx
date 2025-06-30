import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

interface Problem {
  id: string
  title: string
  difficulty: string
  category: string
  description: string
}

interface ProblemStats {
  total: number
  by_difficulty: Record<string, number>
  by_category: Record<string, number>
}

const ProblemsPage: React.FC = () => {
  const navigate = useNavigate()
  const [problems, setProblems] = useState<Problem[]>([])
  const [stats, setStats] = useState<ProblemStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  useEffect(() => {
    fetchProblems()
    fetchStats()
  }, [])

  const fetchProblems = async () => {
    try {
      const response = await fetch('/api/v1/explanation/problems')
      if (response.ok) {
        const data = await response.json()
        setProblems(data.problems)
      }
    } catch (error) {
      console.error('Error fetching problems:', error)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/v1/explanation/stats')
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'text-green-600 bg-green-100 border-green-300'
      case 'intermediate': return 'text-yellow-600 bg-yellow-100 border-yellow-300'
      case 'advanced': return 'text-red-600 bg-red-100 border-red-300'
      default: return 'text-gray-600 bg-gray-100 border-gray-300'
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'runtime_error': return '💥'
      case 'logic_error': return '🤔'
      case 'security': return '🔒'
      case 'resource_management': return '📦'
      case 'concurrency': return '⚡'
      default: return '🐛'
    }
  }

  const filteredProblems = problems.filter(problem => {
    const difficultyMatch = selectedDifficulty === 'all' || problem.difficulty === selectedDifficulty
    const categoryMatch = selectedCategory === 'all' || problem.category === selectedCategory
    return difficultyMatch && categoryMatch
  })

  const startProblem = (difficulty: string) => {
    navigate('/', { state: { selectedDifficulty: difficulty } })
  }

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading problems...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">📚 Problem Library</h1>
        <p className="text-gray-600 text-lg">
          Explore all available coding challenges and learn from detailed explanations
        </p>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-blue-600">{stats.total}</div>
            <div className="text-sm text-gray-600">Total Problems</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-green-600">{stats.by_difficulty.beginner || 0}</div>
            <div className="text-sm text-gray-600">Beginner</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-yellow-600">{stats.by_difficulty.intermediate || 0}</div>
            <div className="text-sm text-gray-600">Intermediate</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-red-600">{stats.by_difficulty.advanced || 0}</div>
            <div className="text-sm text-gray-600">Advanced</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="font-semibold text-lg mb-4">🔍 Filter Problems</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Difficulties</option>
              <option value="beginner">🟢 Beginner</option>
              <option value="intermediate">🟡 Intermediate</option>
              <option value="advanced">🔴 Advanced</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Categories</option>
              <option value="runtime_error">💥 Runtime Errors</option>
              <option value="logic_error">🤔 Logic Errors</option>
              <option value="security">🔒 Security Issues</option>
              <option value="resource_management">📦 Resource Management</option>
              <option value="concurrency">⚡ Concurrency</option>
            </select>
          </div>
        </div>
      </div>

      {/* Problems Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProblems.map((problem) => (
          <div key={problem.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
            <div className="p-6">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">{getCategoryIcon(problem.category)}</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium border ${getDifficultyColor(problem.difficulty)}`}>
                    {problem.difficulty}
                  </span>
                </div>
              </div>
              
              <h3 className="font-semibold text-lg text-gray-900 mb-2">{problem.title}</h3>
              <p className="text-gray-600 text-sm mb-4 line-clamp-3">{problem.description}</p>
              
              <div className="text-xs text-gray-500 mb-4">
                Category: {problem.category.replace('_', ' ').toUpperCase()}
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => navigate(`/explanation/${problem.id}`)}
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 text-sm font-medium"
                >
                  📖 View Explanation
                </button>
                <button
                  onClick={() => startProblem(problem.difficulty)}
                  className="flex-1 bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 text-sm font-medium"
                >
                  🎮 Practice
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredProblems.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Problems Found</h3>
          <p className="text-gray-600 mb-6">Try adjusting your filters to see more problems.</p>
          <button
            onClick={() => {
              setSelectedDifficulty('all')
              setSelectedCategory('all')
            }}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            Clear Filters
          </button>
        </div>
      )}

      {/* Quick Start Section */}
      <div className="mt-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-8 text-white text-center">
        <h2 className="text-2xl font-bold mb-4">🚀 Ready to Start Coding?</h2>
        <p className="mb-6">Jump into a challenge and test your bug-finding skills!</p>
        <div className="flex justify-center space-x-4">
          <button
            onClick={() => startProblem('beginner')}
            className="bg-white text-blue-600 px-6 py-3 rounded-lg hover:bg-gray-100 font-semibold"
          >
            🟢 Start Beginner
          </button>
          <button
            onClick={() => startProblem('intermediate')}
            className="bg-white text-purple-600 px-6 py-3 rounded-lg hover:bg-gray-100 font-semibold"
          >
            🟡 Try Intermediate
          </button>
          <button
            onClick={() => startProblem('advanced')}
            className="bg-white text-red-600 px-6 py-3 rounded-lg hover:bg-gray-100 font-semibold"
          >
            🔴 Challenge Advanced
          </button>
        </div>
      </div>
    </div>
  )
}

export default ProblemsPage
