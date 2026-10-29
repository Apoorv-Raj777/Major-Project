import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { FileText, TrendingUp, MessageSquare, Upload } from 'lucide-react'

export default function ApplicantDashboard() {
  const [resumes, setResumes] = useState([])
  const [matches, setMatches] = useState([])
  const [feedback, setFeedback] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [resumesRes, matchesRes, feedbackRes] = await Promise.all([
        axios.get('/api/resumes'),
        axios.get('/api/matches/resume/1'), // Simplified - should get all user's matches
        axios.get('/api/feedback/resume/1') // Simplified
      ])
      setResumes(resumesRes.data)
      setMatches(matchesRes.data)
      setFeedback(feedbackRes.data)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <FileText className="h-8 w-8 text-primary-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Resumes Uploaded</p>
              <p className="text-2xl font-bold text-gray-900">{resumes.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Job Matches</p>
              <p className="text-2xl font-bold text-gray-900">{matches.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <MessageSquare className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Feedback Received</p>
              <p className="text-2xl font-bold text-gray-900">{feedback.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link
          to="/applicant/upload-resume"
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center">
            <Upload className="h-10 w-10 text-primary-600" />
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Upload Resume</h3>
              <p className="text-sm text-gray-500">Add a new resume to your profile</p>
            </div>
          </div>
        </Link>

        <Link
          to="/applicant/my-scores"
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center">
            <TrendingUp className="h-10 w-10 text-green-600" />
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">View ATS Scores</h3>
              <p className="text-sm text-gray-500">See how your resume matches job postings</p>
            </div>
          </div>
        </Link>
      </div>

      {/* Recent Feedback */}
      {feedback.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Recent Feedback</h2>
          </div>
          <ul className="divide-y divide-gray-200">
            {feedback.slice(0, 3).map((item) => (
              <li key={item.id} className="px-6 py-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-900">{item.rejection_reason}</h3>
                  <p className="text-sm text-gray-500 mt-1">{item.suggestions}</p>
                  <p className="text-xs text-gray-400 mt-2">
                    {new Date(item.created_at).toLocaleDateString()}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
