import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import axios from 'axios'
import { ArrowLeft, TrendingUp, AlertCircle, CheckCircle, XCircle } from 'lucide-react'

export default function JobDetail() {
  const { id } = useParams()
  const [job, setJob] = useState(null)
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedMatch, setSelectedMatch] = useState(null)
  const [feedback, setFeedback] = useState({ rejection_reason: '', suggestions: '' })
  const [showFeedbackModal, setShowFeedbackModal] = useState(false)

  useEffect(() => {
    fetchJobDetail()
    fetchMatches()
  }, [id])

  const fetchJobDetail = async () => {
    try {
      const response = await axios.get(`/api/jobs/${id}`)
      setJob(response.data)
    } catch (error) {
      console.error('Error fetching job:', error)
    }
  }

  const fetchMatches = async () => {
    try {
      const response = await axios.get(`/api/matches/job/${id}`)
      setMatches(response.data)
    } catch (error) {
      console.error('Error fetching matches:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleVerify = async (matchId) => {
    try {
      await axios.post(`/api/verification/verify/${matchId}`)
      fetchMatches()
    } catch (error) {
      console.error('Error verifying:', error)
    }
  }

  const handleGenerateFeedback = async (matchId) => {
    try {
      const response = await axios.post(`/api/feedback/generate-suggestion/${matchId}`)
      setFeedback({ ...feedback, suggestions: response.data.suggestion })
    } catch (error) {
      console.error('Error generating feedback:', error)
    }
  }

  const handleSubmitFeedback = async () => {
    try {
      await axios.post('/api/feedback', {
        job_id: parseInt(id),
        resume_id: selectedMatch.resume_id,
        ...feedback
      })
      setShowFeedbackModal(false)
      setFeedback({ rejection_reason: '', suggestions: '' })
    } catch (error) {
      console.error('Error submitting feedback:', error)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  if (!job) {
    return <div className="text-center py-12">Job not found</div>
  }

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <Link to="/dashboard" className="inline-flex items-center text-gray-600 hover:text-gray-900">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Link>
      </div>

      {/* Job Info */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">{job.title}</h1>
        </div>
        <div className="p-6">
          <div className="mb-4">
            <h3 className="text-sm font-medium text-gray-500">Description</h3>
            <p className="mt-1 text-gray-900">{job.description}</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Required Skills</h3>
              <div className="mt-1 flex flex-wrap gap-2">
                {job.required_skills?.map((skill, idx) => (
                  <span key={idx} className="px-2 py-1 bg-primary-100 text-primary-700 rounded text-sm">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Min Experience</h3>
              <p className="mt-1 text-gray-900">{job.min_experience_years}+ years</p>
            </div>
          </div>
        </div>
      </div>

      {/* Ranked Candidates */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Ranked Candidates</h2>
        </div>

        {matches.length === 0 ? (
          <div className="px-6 py-12 text-center text-gray-500">
            <TrendingUp className="mx-auto h-12 w-12 text-gray-300 mb-4" />
            <p className="text-lg font-medium">No candidates yet</p>
            <p className="text-sm">Candidates will appear here when resumes are matched to this job</p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {matches.map((match) => (
              <li key={match.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        <div className="h-12 w-12 rounded-full bg-primary-100 flex items-center justify-center">
                          <span className="text-primary-600 font-bold">
                            {match.resume.structured?.name?.charAt(0) || 'C'}
                          </span>
                        </div>
                      </div>
                      <div>
                        <h3 className="text-lg font-medium text-gray-900">
                          {match.resume.structured?.name || 'Candidate'}
                        </h3>
                        <p className="text-sm text-gray-500">
                          Resume: {match.resume.file_name}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-8">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-primary-600">
                        {(match.ats_score * 100).toFixed(0)}%
                      </p>
                      <p className="text-xs text-gray-500">ATS Score</p>
                    </div>

                    <div className="text-center">
                      <p className="text-sm font-medium text-gray-900">
                        {(match.semantic_score * 100).toFixed(0)}%
                      </p>
                      <p className="text-xs text-gray-500">Semantic</p>
                    </div>

                    <div className="text-center">
                      <p className="text-sm font-medium text-gray-900">
                        {(match.skill_score * 100).toFixed(0)}%
                      </p>
                      <p className="text-xs text-gray-500">Skills</p>
                    </div>

                    {match.verification_report?.verified_skill_pct !== undefined && (
                      <div className="text-center">
                        <p className="text-sm font-medium text-gray-900">
                          {(match.verification_report.verified_skill_pct * 100).toFixed(0)}%
                        </p>
                        <p className="text-xs text-gray-500">Verified</p>
                      </div>
                    )}

                    <div className="flex space-x-2">
                      {!match.verification_report && (
                        <button
                          onClick={() => handleVerify(match.id)}
                          className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                        >
                          Verify
                        </button>
                      )}
                      <button
                        onClick={() => {
                          setSelectedMatch(match)
                          setShowFeedbackModal(true)
                        }}
                        className="px-3 py-1 text-sm bg-primary-600 text-white rounded hover:bg-primary-700"
                      >
                        Feedback
                      </button>
                    </div>
                  </div>
                </div>

                {match.verification_report && (
                  <div className="mt-4 p-3 bg-gray-50 rounded">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Verification Report</h4>
                    {match.verification_report.unverified_skills?.length > 0 && (
                      <div className="flex items-center text-sm text-orange-600 mb-1">
                        <AlertCircle className="h-4 w-4 mr-1" />
                        <span>Unverified skills: {match.verification_report.unverified_skills.join(', ')}</span>
                      </div>
                    )}
                    {match.verification_report.timeline_flags?.length > 0 && (
                      <div className="flex items-center text-sm text-red-600">
                        <XCircle className="h-4 w-4 mr-1" />
                        <span>Timeline flags: {match.verification_report.timeline_flags.length}</span>
                      </div>
                    )}
                    {match.verification_report.unverified_skills?.length === 0 && match.verification_report.timeline_flags?.length === 0 && (
                      <div className="flex items-center text-sm text-green-600">
                        <CheckCircle className="h-4 w-4 mr-1" />
                        <span>All skills verified, no timeline issues</span>
                      </div>
                    )}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Feedback Modal */}
      {showFeedbackModal && selectedMatch && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Send Feedback</h3>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Rejection Reason</label>
                <textarea
                  rows={3}
                  value={feedback.rejection_reason}
                  onChange={(e) => setFeedback({ ...feedback, rejection_reason: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Suggestions</label>
                <textarea
                  rows={3}
                  value={feedback.suggestions}
                  onChange={(e) => setFeedback({ ...feedback, suggestions: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                />
                <button
                  type="button"
                  onClick={() => handleGenerateFeedback(selectedMatch.id)}
                  className="mt-2 text-sm text-primary-600 hover:text-primary-700"
                >
                  Generate AI suggestion
                </button>
              </div>
            </div>
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowFeedbackModal(false)
                  setFeedback({ rejection_reason: '', suggestions: '' })
                }}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmitFeedback}
                className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
              >
                Send Feedback
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
