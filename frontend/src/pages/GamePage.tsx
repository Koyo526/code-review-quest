import React, { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import Editor from '@monaco-editor/react'

interface BugReport {
  line_number: number
  description?: string
}

const GamePage: React.FC = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const session = location.state?.session

  const [bugs, setBugs] = useState<BugReport[]>([])
  const [timeLeft, setTimeLeft] = useState(session?.time_limit || 900)
  const [selectedLine, setSelectedLine] = useState<number | null>(null)

  useEffect(() => {
    if (!session) {
      navigate('/')
      return
    }

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          handleSubmit()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [session, navigate])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const handleEditorClick = (e: any) => {
    const lineNumber = e.target.position?.lineNumber
    if (lineNumber) {
      setSelectedLine(lineNumber)
    }
  }

  const addBugReport = () => {
    if (selectedLine && !bugs.find(bug => bug.line_number === selectedLine)) {
      setBugs([...bugs, { line_number: selectedLine }])
      setSelectedLine(null)
    }
  }

  const removeBugReport = (lineNumber: number) => {
    setBugs(bugs.filter(bug => bug.line_number !== lineNumber))
  }

  const handleSubmit = async () => {
    try {
      const response = await fetch('/api/v1/submit/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: session.session_id,
          bugs: bugs,
        }),
      })

      if (response.ok) {
        const result = await response.json()
        navigate('/result', { state: { result, session } })
      }
    } catch (error) {
      console.error('Error submitting:', error)
    }
  }

  if (!session) {
    return <div>Loading...</div>
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Code Review Challenge</h1>
          <p className="text-gray-600">
            Difficulty: <span className="font-semibold">{session.difficulty}</span>
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className={`text-lg font-mono ${timeLeft < 60 ? 'text-red-600' : 'text-gray-700'}`}>
            ⏱️ {formatTime(timeLeft)}
          </div>
          <button
            onClick={handleSubmit}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Submit ({bugs.length} bugs)
          </button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="p-4 bg-gray-50 border-b">
              <h3 className="font-semibold">Code to Review</h3>
              <p className="text-sm text-gray-600">Click on a line number to report a bug</p>
            </div>
            <div className="h-96">
              <Editor
                height="100%"
                defaultLanguage="python"
                value={session.code}
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  lineNumbers: 'on',
                  glyphMargin: true,
                }}
                onMount={(editor) => {
                  editor.onMouseDown(handleEditorClick)
                }}
              />
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="font-semibold mb-3">Bug Reports</h3>
            
            {selectedLine && (
              <div className="mb-4 p-3 bg-blue-50 rounded border">
                <p className="text-sm text-blue-800">
                  Selected line: {selectedLine}
                </p>
                <button
                  onClick={addBugReport}
                  className="mt-2 bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                >
                  Report Bug
                </button>
              </div>
            )}

            <div className="space-y-2">
              {bugs.length === 0 ? (
                <p className="text-gray-500 text-sm">No bugs reported yet</p>
              ) : (
                bugs.map((bug) => (
                  <div key={bug.line_number} className="flex justify-between items-center p-2 bg-red-50 rounded">
                    <span className="text-sm">Line {bug.line_number}</span>
                    <button
                      onClick={() => removeBugReport(bug.line_number)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="font-semibold mb-3">Instructions</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Click on line numbers to select them</li>
              <li>• Report bugs by clicking "Report Bug"</li>
              <li>• Look for syntax errors, logic bugs, and edge cases</li>
              <li>• Submit before time runs out!</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GamePage
