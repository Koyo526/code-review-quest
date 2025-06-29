import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const HomePage: React.FC = () => {
  const [difficulty, setDifficulty] = useState('beginner')
  const [timeLimit, setTimeLimit] = useState(900)
  const navigate = useNavigate()

  const handleStartGame = async () => {
    try {
      const response = await fetch('/api/v1/session/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          difficulty,
          time_limit: timeLimit,
        }),
      })

      if (response.ok) {
        const session = await response.json()
        navigate('/game', { state: { session } })
      } else {
        console.error('Failed to start session')
      }
    } catch (error) {
      console.error('Error starting session:', error)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to Code Review Quest! 🎮
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Sharpen your bug-finding skills through interactive code challenges
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-8 max-w-2xl mx-auto">
        <h2 className="text-2xl font-semibold mb-6">Start New Challenge</h2>
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Difficulty Level
            </label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="beginner">🟢 Beginner - Basic syntax errors</option>
              <option value="intermediate">🟡 Intermediate - Logic bugs</option>
              <option value="advanced">🔴 Advanced - Complex design issues</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Time Limit
            </label>
            <select
              value={timeLimit}
              onChange={(e) => setTimeLimit(Number(e.target.value))}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={300}>5 minutes - Quick challenge</option>
              <option value={900}>15 minutes - Standard</option>
              <option value={1800}>30 minutes - Extended</option>
            </select>
          </div>

          <button
            onClick={handleStartGame}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 transition-colors font-semibold text-lg"
          >
            🚀 Start Challenge
          </button>
        </div>
      </div>

      <div className="mt-12 grid md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md text-center">
          <div className="text-3xl mb-2">🔍</div>
          <h3 className="font-semibold mb-2">Find Bugs</h3>
          <p className="text-gray-600">Identify syntax errors, logic bugs, and design issues</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md text-center">
          <div className="text-3xl mb-2">⏱️</div>
          <h3 className="font-semibold mb-2">Beat the Clock</h3>
          <p className="text-gray-600">Race against time to maximize your score</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md text-center">
          <div className="text-3xl mb-2">🏆</div>
          <h3 className="font-semibold mb-2">Earn Badges</h3>
          <p className="text-gray-600">Unlock achievements and climb the leaderboard</p>
        </div>
      </div>
    </div>
  )
}

export default HomePage
