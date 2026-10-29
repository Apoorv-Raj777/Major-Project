import { useState, useEffect } from 'react'
import axios from 'axios'
import { TrendingUp, AlertCircle, CheckCircle } from 'lucide-react'

export default function MyScores() {
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMatches()
  }, [])

  const fetchMatches = async () => {
    try {
      const response = await axios.get('/api/matches/resume/1') // Simplified
      setMatches(response.data)
    } catch (error) {
      console.error('Error fetching matches:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">My ATS Scores</h1>
        </div>

        {matches.length === 0 ? (
          <div className="px-6 py-12 text-center text-gray-500">
            <TrendingUp className="mx-auto h-12 w-12 text-gray-300 mb-4" />
            <p className="text-lg font-medium">No scores yet</p>
            <p className="text-sm">Upload a resume to see how it matches job postings</p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {matches.map((match) => (
              <li key={match.id} className="px-6 py-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900">
                      {match.job.title}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">
                      {match.job.description?.substring(0, 150)}...
                    </p>
                  </div>

                  <div className="ml-6 text-center">
                    <div className={`text-4xl font-bold ${
                      match.ats_score >= 0.7 ? 'text-green-600' :
                      match.ats_score >= 0.5 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {(match.ats_score * 100).toFixed(0)}%
                    </div>
                    <p className="text-sm text-gray-500">Overall Score</p>
                  </div>
                </div>

                {/* Score Breakdown */}
                <div className="mt-6 grid grid-cols-3 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Semantic Match</span>
                      <span className="text-sm font-bold text-gray-900">
                        {(match.semantic_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full"
                        style={{ width: `${match.semantic_score * 100}%` }}
                      />
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Skill Match</span>
                      <span className="text-sm font-bold text-gray-900">
                        {(match.skill_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full"
                        style={{ width: `${match.skill_score * 100}%` }}
                      />
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Experience</span>
                      <span className="text-sm font-bold text-gray-900">
                        {(match.experience_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-purple-600 h-2 rounded-full"
                        style={{ width: `${match.experience_score * 100}%` }}
                      />
                    </div>
                  </div>
                </div>

                {/* Missing Skills */}
                {match.skill_score < 1.0 && (
                  <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div className="flex items-start">
                      <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5 mr-2" />
                      <div>
                        <h4 className="text-sm font-medium text-yellow-900">Missing Skills</h4>
                        <p className="text-sm text-yellow-800 mt-1">
                          Your semantic match was strong, but you may be missing some required skills.
                          Consider adding: {match.job.required_skills?.slice(0, 3).join(', ')}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {match.ats_score >= 0.7 && (
                  <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 mr-2" />
                      <div>
                        <h4 className="text-sm font-medium text-green-900">Strong Match!</h4>
                        <p className="text-sm text-green-800 mt-1">
                          Your resume is a good fit for this position. Keep up the great work!
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
