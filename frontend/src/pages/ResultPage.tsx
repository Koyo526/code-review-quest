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
              {result.correct_bugs?.length || 0}
            </div>
            <div className="text-sm text-green-800">Bugs Found</div>
          </div>
          
          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">
              {result.missed_bugs?.length || 0}
            </div>
            <div className="text-sm text-yellow-800">Bugs Missed</div>
          </div>
          
          <div className="text-center p-4 bg-red-50 rounded-lg">
            <div className="text-2xl font-bold text-red-600">
              {result.false_positives?.length || 0}
            </div>
            <div className="text-sm text-red-800">False Positives</div>
          </div>
        </div>

        {/* Detailed Feedback */}
        {result.detailed_feedback && result.detailed_feedback.length > 0 && (
          <div className="mb-8">
            <h3 className="font-semibold mb-4 text-lg">📋 Detailed Feedback</h3>
            <div className="space-y-3">
              {result.detailed_feedback.map((feedback: any, index: number) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border-l-4 ${
                    feedback.status === 'correct' ? 'bg-green-50 border-green-400' :
                    feedback.status === 'missed' ? 'bg-yellow-50 border-yellow-400' :
                    'bg-red-50 border-red-400'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="font-medium text-sm">{feedback.message}</p>
                      <p className="text-sm text-gray-600 mt-1">{feedback.explanation}</p>
                      {feedback.fix_suggestion && (
                        <div className="mt-2 p-2 bg-blue-50 rounded text-sm">
                          <strong>💡 Fix:</strong> {feedback.fix_suggestion}
                        </div>
                      )}
                    </div>
                    <span className="text-xs bg-gray-100 px-2 py-1 rounded ml-2">
                      Line {feedback.line_number}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

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

        {/* Link to detailed explanation */}
        {result.problem_id && (
          <button
            onClick={() => navigate(`/explanation/${result.problem_id}`)}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 font-semibold"
          >
            📖 View Explanation
          </button>
        )}

        <button
          onClick={() => navigate('/problems')}
          className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-semibold"
        >
          📚 Browse Problems
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
