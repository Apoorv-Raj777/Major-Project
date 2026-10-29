import { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingUp, AlertTriangle, CheckCircle, RefreshCw } from 'lucide-react'

export default function FairnessDashboard() {
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [recording, setRecording] = useState(false)

  useEffect(() => {
    fetchMetrics()
  }, [])

  const fetchMetrics = async () => {
    try {
      const response = await axios.get('/api/fairness/dashboard')
      setMetrics(response.data)
    } catch (error) {
      console.error('Error fetching fairness metrics:', error)
    } finally {
      setLoading(false)
    }
  }

  const recordMetrics = async () => {
    setRecording(true)
    try {
      await axios.post('/api/fairness/record-metrics')
      alert('Fairness metrics recorded successfully')
    } catch (error) {
      console.error('Error recording metrics:', error)
      alert('Failed to record metrics')
    } finally {
      setRecording(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading fairness metrics...</div>
  }

  if (!metrics) {
    return <div className="text-center py-12">No data available</div>
  }

  // Prepare chart data
  const chartData = metrics.by_language.map(lang => ({
    language: lang.language_code || 'Unknown',
    avgScore: (lang.average_ats_score * 100).toFixed(1),
    shortlistRate: (lang.shortlist_rate * 100).toFixed(1),
    totalResumes: lang.total_resumes
  }))

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Fairness Dashboard</h1>
        <button
          onClick={recordMetrics}
          disabled={recording}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${recording ? 'animate-spin' : ''}`} />
          {recording ? 'Recording...' : 'Record Metrics'}
        </button>
      </div>

      {/* Overall Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-primary-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Overall Average ATS Score</p>
              <p className="text-2xl font-bold text-gray-900">
                {(metrics.overall.average_ats_score * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Resumes Processed</p>
              <p className="text-2xl font-bold text-gray-900">
                {metrics.overall.total_resumes}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Equity Analysis Alert */}
      <div className={`${
        metrics.equity_analysis.disparity_flag 
          ? 'bg-red-50 border-red-200' 
          : 'bg-green-50 border-green-200'
      } border rounded-lg p-4`}>
        <div className="flex items-start">
          {metrics.equity_analysis.disparity_flag ? (
            <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5 mr-2 flex-shrink-0" />
          ) : (
            <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 mr-2 flex-shrink-0" />
          )}
          <div>
            <h3 className={`text-sm font-medium ${
              metrics.equity_analysis.disparity_flag ? 'text-red-900' : 'text-green-900'
            }`}>
              {metrics.equity_analysis.disparity_flag ? 'Equity Alert' : 'Equity Check Passed'}
            </h3>
            <p className={`text-sm mt-1 ${
              metrics.equity_analysis.disparity_flag ? 'text-red-800' : 'text-green-800'
            }`}>
              {metrics.equity_analysis.interpretation}
            </p>
            <p className="text-xs mt-1 text-gray-600">
              Rate disparity: {(metrics.equity_analysis.rate_disparity * 100).toFixed(1)}%
            </p>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Average ATS Score by Language */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Average ATS Score by Language
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="language" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="avgScore" name="Avg ATS Score (%)" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Shortlist Rate by Language */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Shortlist Rate by Language
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="language" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="shortlistRate" name="Shortlist Rate (%)" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Detailed Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Detailed Metrics by Language</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Language
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Resumes
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg ATS Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Shortlisted
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Shortlist Rate
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {metrics.by_language.map((lang, idx) => (
                <tr key={idx}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {lang.language_code || 'Unknown'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {lang.total_resumes}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {(lang.average_ats_score * 100).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {lang.shortlisted_count}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {(lang.shortlist_rate * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Info Banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-900 mb-2">About Fairness Metrics</h3>
        <ul className="text-xs text-blue-800 space-y-1 list-disc list-inside">
          <li>These metrics track ATS scores and shortlist rates across detected languages</li>
          <li>A rate disparity above 20% triggers an equity alert for review</li>
          <li>This helps ensure the system doesn't systematically disadvantage any language group</li>
          <li>Protected attributes (gender, age, ethnicity) are never used as model features</li>
        </ul>
      </div>
    </div>
  )
}
