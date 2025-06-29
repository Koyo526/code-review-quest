import React, { useState, useEffect } from 'react'

interface Profile {
  user_id: string
  username: string
  stats: {
    total_sessions: number
    average_score: number
    best_score: number
    total_bugs_found: number
    accuracy_rate: number
    favorite_difficulty: string
  }
  badges: Array<{
    id: string
    name: string
    description: string
    earned_at: number
  }>
  recent_scores: number[]
}

const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [leaderboard, setLeaderboard] = useState<any[]>([])

  useEffect(() => {
    fetchProfile()
    fetchLeaderboard()
  }, [])

  const fetchProfile = async () => {
    try {
      const response = await fetch('/api/v1/profile/me')
      if (response.ok) {
        const data = await response.json()
        setProfile(data)
      }
    } catch (error) {
      console.error('Error fetching profile:', error)
    }
  }

  const fetchLeaderboard = async () => {
    try {
      const response = await fetch('/api/v1/profile/leaderboard')
      if (response.ok) {
        const data = await response.json()
        setLeaderboard(data.leaderboard)
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error)
    }
  }

  if (!profile) {
    return <div className="text-center py-8">Loading profile...</div>
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome back, {profile.username}! 👋
        </h1>
        <p className="text-gray-600">Track your progress and achievements</p>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          {/* Stats Overview */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Performance Statistics</h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {profile.stats.total_sessions}
                </div>
                <div className="text-sm text-blue-800">Total Sessions</div>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {profile.stats.average_score.toFixed(1)}
                </div>
                <div className="text-sm text-green-800">Average Score</div>
              </div>
              
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {profile.stats.best_score}
                </div>
                <div className="text-sm text-purple-800">Best Score</div>
              </div>
              
              <div className="bg-yellow-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {(profile.stats.accuracy_rate * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-yellow-800">Accuracy Rate</div>
              </div>
            </div>
          </div>

          {/* Recent Scores */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Recent Performance</h2>
            <div className="flex space-x-2">
              {profile.recent_scores.map((score, index) => (
                <div
                  key={index}
                  className={`px-3 py-2 rounded text-sm font-medium ${
                    score >= 90 ? 'bg-green-100 text-green-800' :
                    score >= 70 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}
                >
                  {score}
                </div>
              ))}
            </div>
          </div>

          {/* Badges */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Achievements 🏆</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {profile.badges.map((badge) => (
                <div key={badge.id} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl">🏅</div>
                    <div>
                      <h3 className="font-semibold">{badge.name}</h3>
                      <p className="text-sm text-gray-600">{badge.description}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        Earned {new Date(badge.earned_at * 1000).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="font-semibold mb-4">Quick Stats</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Bugs Found</span>
                <span className="font-semibold">{profile.stats.total_bugs_found}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Favorite Difficulty</span>
                <span className="font-semibold capitalize">{profile.stats.favorite_difficulty}</span>
              </div>
            </div>
          </div>

          {/* Leaderboard */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="font-semibold mb-4">🏆 Leaderboard</h3>
            <div className="space-y-2">
              {leaderboard.map((player) => (
                <div
                  key={player.rank}
                  className={`flex justify-between items-center p-2 rounded ${
                    player.username === profile.username ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium">#{player.rank}</span>
                    <span className="text-sm">{player.username}</span>
                  </div>
                  <span className="text-sm font-semibold">{player.score}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage
