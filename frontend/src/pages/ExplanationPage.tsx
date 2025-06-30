import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Editor from '@monaco-editor/react'

interface Bug {
  line_number: number
  type: string
  severity: string
  description: string
  explanation: string
  fix_suggestion: string
}

interface TestCase {
  input?: string
  expected_output?: string
  expected_error?: string
  expected_vulnerability?: string
}

interface ExplanationData {
  problem_id: string
  title: string
  difficulty: string
  category: string
  description: string
  code: string
  bugs: Bug[]
  test_cases: TestCase[]
  learning_objectives: string[]
  detailed_explanation: string
}

const ExplanationPage: React.FC = () => {
  const { problemId } = useParams<{ problemId: string }>()
  const navigate = useNavigate()
  const [explanation, setExplanation] = useState<ExplanationData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedBugLine, setSelectedBugLine] = useState<number | null>(null)

  useEffect(() => {
    if (problemId) {
      fetchExplanation(problemId)
    }
  }, [problemId])

  const fetchExplanation = async (id: string) => {
    try {
      const response = await fetch(`/api/v1/explanation/problem/${id}`)
      if (response.ok) {
        const data = await response.json()
        setExplanation(data)
      } else {
        setError('Problem not found')
      }
    } catch (err) {
      setError('Failed to load explanation')
    } finally {
      setLoading(false)
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'text-green-600 bg-green-100'
      case 'intermediate': return 'text-yellow-600 bg-yellow-100'
      case 'advanced': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-700 bg-red-100 border-red-300'
      case 'high': return 'text-red-600 bg-red-50 border-red-200'
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'low': return 'text-green-600 bg-green-50 border-green-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const highlightBugLines = (code: string, bugs: Bug[]) => {
    const lines = code.split('\n')
    const bugLines = bugs.map(bug => bug.line_number)
    
    return lines.map((line, index) => {
      const lineNumber = index + 1
      const isBugLine = bugLines.includes(lineNumber)
      const isSelected = selectedBugLine === lineNumber
      
      return (
        <div
          key={index}
          className={`flex ${isBugLine ? 'bg-red-50 border-l-4 border-red-400' : ''} ${
            isSelected ? 'bg-blue-50' : ''
          }`}
          onClick={() => setSelectedBugLine(isBugLine ? lineNumber : null)}
        >
          <span className="w-8 text-right text-gray-500 text-sm pr-2 select-none">
            {lineNumber}
          </span>
          <span className={`flex-1 ${isBugLine ? 'font-medium' : ''}`}>
            {line}
          </span>
          {isBugLine && (
            <span className="text-red-500 text-sm px-2">🐛</span>
          )}
        </div>
      )
    })
  }

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading explanation...</p>
        </div>
      </div>
    )
  }

  if (error || !explanation) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center">
          <div className="text-red-600 text-6xl mb-4">❌</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Problem Not Found</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            Back to Home
          </button>
        </div>
      </div>
    )
  }

  const selectedBug = explanation.bugs.find(bug => bug.line_number === selectedBugLine)

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={() => navigate(-1)}
            className="text-blue-600 hover:text-blue-800 flex items-center"
          >
            ← Back
          </button>
          <div className="flex items-center space-x-2">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(explanation.difficulty)}`}>
              {explanation.difficulty}
            </span>
            <span className="px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-700">
              {explanation.category.replace('_', ' ')}
            </span>
          </div>
        </div>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{explanation.title}</h1>
        <p className="text-gray-600 text-lg">{explanation.description}</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Code Section */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="bg-gray-50 px-4 py-3 border-b">
              <h2 className="font-semibold text-gray-900">Code Analysis</h2>
              <p className="text-sm text-gray-600">Click on highlighted lines to see bug details</p>
            </div>
            <div className="p-4">
              <div className="bg-gray-900 text-gray-100 p-4 rounded font-mono text-sm overflow-x-auto">
                <pre className="whitespace-pre-wrap">
                  {highlightBugLines(explanation.code, explanation.bugs)}
                </pre>
              </div>
            </div>
          </div>

          {/* Selected Bug Details */}
          {selectedBug && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="font-semibold text-lg mb-4">
                🐛 Bug Details - Line {selectedBug.line_number}
              </h3>
              <div className="space-y-3">
                <div className={`px-3 py-2 rounded border ${getSeverityColor(selectedBug.severity)}`}>
                  <span className="font-medium">{selectedBug.severity.toUpperCase()} SEVERITY</span>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Description:</h4>
                  <p className="text-gray-700">{selectedBug.description}</p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Explanation:</h4>
                  <p className="text-gray-700">{selectedBug.explanation}</p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Fix Suggestion:</h4>
                  <p className="text-gray-700 bg-green-50 p-3 rounded border-l-4 border-green-400">
                    {selectedBug.fix_suggestion}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Explanation Section */}
        <div className="space-y-6">
          {/* Bug Summary */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="font-semibold text-lg mb-4">🎯 Bug Summary</h2>
            <div className="space-y-3">
              {explanation.bugs.map((bug, index) => (
                <div
                  key={index}
                  className={`p-3 rounded border cursor-pointer transition-colors ${
                    selectedBugLine === bug.line_number ? 'bg-blue-50 border-blue-300' : 'hover:bg-gray-50'
                  } ${getSeverityColor(bug.severity)}`}
                  onClick={() => setSelectedBugLine(bug.line_number)}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="font-medium">Line {bug.line_number}</span>
                      <span className="text-sm ml-2">({bug.type.replace('_', ' ')})</span>
                    </div>
                    <span className="text-xs font-medium px-2 py-1 rounded">
                      {bug.severity}
                    </span>
                  </div>
                  <p className="text-sm mt-1">{bug.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Test Cases */}
          {explanation.test_cases.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="font-semibold text-lg mb-4">🧪 Test Cases</h2>
              <div className="space-y-3">
                {explanation.test_cases.map((testCase, index) => (
                  <div key={index} className="bg-gray-50 p-3 rounded">
                    <h4 className="font-medium text-sm text-gray-700">Test Case #{index + 1}</h4>
                    {testCase.input && (
                      <p className="text-sm"><strong>Input:</strong> {testCase.input}</p>
                    )}
                    {testCase.expected_output && (
                      <p className="text-sm text-green-700"><strong>Expected:</strong> {testCase.expected_output}</p>
                    )}
                    {testCase.expected_error && (
                      <p className="text-sm text-red-700"><strong>Error:</strong> {testCase.expected_error}</p>
                    )}
                    {testCase.expected_vulnerability && (
                      <p className="text-sm text-orange-700"><strong>Vulnerability:</strong> {testCase.expected_vulnerability}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Learning Objectives */}
          {explanation.learning_objectives.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="font-semibold text-lg mb-4">📚 Learning Objectives</h2>
              <ul className="space-y-2">
                {explanation.learning_objectives.map((objective, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-blue-500 mr-2">•</span>
                    <span className="text-gray-700">{objective}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-8 flex justify-center space-x-4">
        <button
          onClick={() => navigate('/')}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-semibold"
        >
          🎮 Try Another Problem
        </button>
        <button
          onClick={() => navigate('/problems')}
          className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 font-semibold"
        >
          📚 Browse All Problems
        </button>
      </div>
    </div>
  )
}

export default ExplanationPage
