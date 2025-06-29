import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

const ResultPage: React.FC = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { result, session } = location.state || {}

  if (!result) {
    navigate('/')
    return null
  }

  const scorePercentage = (result.score / result.max_score) * 100

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Challenge Complete! 🎉</h1>
        <p className="text-gray-600">Here's how you performed</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-8 mb-8">
        <div className="text-center mb-6">
          <div className="text-6xl font-bold text-blue-600 mb-2">
            {result.score}
          </div>
          <div className="text-xl text-gray-600">
            out of {result.max_score} points ({scorePercentage.toFixed(1)}%)
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {result.correct_bugs.length}
            </div>
            <div className="text-sm text-green-800">Bugs Found</div>
          </div>
          
          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">
              {result.missed_bugs.length}
            </div>
            <div className="text-sm text-yellow-800">Bugs Missed</div>
          </div>
          
          <div className="text-center p-4 bg-red-50 rounded-lg">
            <div className="text-2xl font-bold text-red-600">
              {result.false_positives.length}
            </div>
            <div className="text-sm text-red-800">False Positives</div>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="font-semibold mb-3">Detailed Analysis</h3>
          <div className="whitespace-pre-line text-sm text-gray-700">
            {result.explanation}
          </div>
        </div>
      </div>

      <div className="flex justify-center space-x-4">
        <button
          onClick={() => navigate('/')}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-semibold"
        >
          🎮 Play Again
        </button>
        
        <button
          onClick={() => navigate('/profile')}
          className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 font-semibold"
        >
          📊 View Profile
        </button>
      </div>

      {scorePercentage >= 90 && (
        <div className="mt-8 text-center">
          <div className="inline-block bg-yellow-100 border border-yellow-300 rounded-lg p-4">
            <div className="text-2xl mb-2">🏆</div>
            <div className="font-semibold text-yellow-800">Excellent Performance!</div>
            <div className="text-sm text-yellow-700">You've earned the "Bug Hunter" badge!</div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ResultPage
