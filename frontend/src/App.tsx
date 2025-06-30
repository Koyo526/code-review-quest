import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import HomePage from './pages/HomePage'
import GamePage from './pages/GamePage'
import ResultPage from './pages/ResultPage'
import ProfilePage from './pages/ProfilePage'
import ExplanationPage from './pages/ExplanationPage'
import ProblemsPage from './pages/ProblemsPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'

const Navigation: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth()

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              🎮 Code Review Quest
            </h1>
          </div>
          <nav className="flex items-center space-x-4">
            <a href="/" className="text-gray-600 hover:text-gray-900">Home</a>
            <a href="/problems" className="text-gray-600 hover:text-gray-900">Problems</a>
            
            {isAuthenticated ? (
              <>
                <a href="/profile" className="text-gray-600 hover:text-gray-900">Profile</a>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">
                    Welcome, {user?.display_name || user?.username}!
                  </span>
                  <button
                    onClick={logout}
                    className="text-sm bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
                  >
                    Logout
                  </button>
                </div>
              </>
            ) : (
              <div className="flex items-center space-x-2">
                <a
                  href="/login"
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  Login
                </a>
                <a
                  href="/register"
                  className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
                >
                  Sign Up
                </a>
              </div>
            )}
          </nav>
        </div>
      </div>
    </header>
  )
}

const AppContent: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/game" element={<GamePage />} />
          <Route path="/result" element={<ResultPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/problems" element={<ProblemsPage />} />
          <Route path="/explanation/:problemId" element={<ExplanationPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Routes>
      </main>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
