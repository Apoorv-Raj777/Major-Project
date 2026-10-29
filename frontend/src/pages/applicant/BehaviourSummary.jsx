import { useState, useEffect } from 'react'
import axios from 'axios'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from 'recharts'
import { Info, AlertTriangle } from 'lucide-react'

export default function BehaviourSummary() {
  const [personality, setPersonality] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPersonality()
  }, [])

  const fetchPersonality = async () => {
    try {
      const response = await axios.get('/api/behaviour/my-personality')
      setPersonality(response.data)
    } catch (error) {
      console.error('Error fetching personality data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  if (!personality) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-center">
            <AlertTriangle className="mx-auto h-12 w-12 text-yellow-500 mb-4" />
            <h2 className="text-lg font-medium text-gray-900 mb-2">No personality data available</h2>
            <p className="text-sm text-gray-500 mb-4">
              Please upload your LinkedIn profile with consent to view your behavioural analysis.
            </p>
            <a
              href="/applicant/upload-linkedin"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              Upload LinkedIn Profile
            </a>
          </div>
        </div>
      </div>
    )
  }

  const radarData = [
    { trait: 'Openness', value: personality.openness * 100 },
    { trait: 'Conscientiousness', value: personality.conscientiousness * 100 },
    { trait: 'Extraversion', value: personality.extraversion * 100 },
    { trait: 'Agreeableness', value: personality.agreeableness * 100 },
    { trait: 'Neuroticism', value: personality.neuroticism * 100 }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start">
          <Info className="h-5 w-5 text-yellow-600 mt-0.5 mr-2 flex-shrink-0" />
          <div>
            <h3 className="text-sm font-medium text-yellow-900">Important Disclaimer</h3>
            <p className="text-sm text-yellow-800 mt-1">
              These personality trait scores are approximate indicators inferred from your LinkedIn profile text using AI. They are NOT clinical assessments and should not be used for hiring decisions in isolation. They are provided for informational purposes only.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">Big Five Personality Profile</h1>
        </div>

        <div className="p-6">
          {/* Radar Chart */}
          <div className="mb-8">
            <h3 className="text-sm font-medium text-gray-700 mb-4 text-center">Personality Trait Overview</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="trait" />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} />
                  <Radar
                    name="Personality"
                    dataKey="value"
                    stroke="#3b82f6"
                    fill="#3b82f6"
                    fillOpacity={0.3}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Trait Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">Openness</h4>
                <span className="text-sm font-bold text-primary-600">
                  {(personality.openness * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-xs text-gray-600">
                Creativity, curiosity, and preference for variety
              </p>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-primary-600 h-2 rounded-full"
                  style={{ width: `${personality.openness * 100}%` }}
                />
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">Conscientiousness</h4>
                <span className="text-sm font-bold text-green-600">
                  {(personality.conscientiousness * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-xs text-gray-600">
                Organization, discipline, and reliability
              </p>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-green-600 h-2 rounded-full"
                  style={{ width: `${personality.conscientiousness * 100}%` }}
                />
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">Extraversion</h4>
                <span className="text-sm font-bold text-purple-600">
                  {(personality.extraversion * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-xs text-gray-600">
                Sociability, energy, and assertiveness
              </p>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-purple-600 h-2 rounded-full"
                  style={{ width: `${personality.extraversion * 100}%` }}
                />
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">Agreeableness</h4>
                <span className="text-sm font-bold text-blue-600">
                  {(personality.agreeableness * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-xs text-gray-600">
                Cooperation, trust, and compassion
              </p>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${personality.agreeableness * 100}%` }}
                />
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 md:col-span-2">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">Neuroticism</h4>
                <span className="text-sm font-bold text-orange-600">
                  {(personality.neuroticism * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-xs text-gray-600">
                Emotional stability and stress response
              </p>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-orange-600 h-2 rounded-full"
                  style={{ width: `${personality.neuroticism * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
