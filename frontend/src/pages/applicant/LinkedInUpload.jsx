import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { Upload, FileText, CheckCircle, AlertCircle, Info } from 'lucide-react'

export default function LinkedInUpload() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [consent, setConsent] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (selectedFile.size > 5 * 1024 * 1024) {
        setError('File size exceeds 5MB limit')
        setFile(null)
        return
      }
      if (!selectedFile.name.endsWith('.pdf')) {
        setError('Only PDF files are allowed for LinkedIn exports')
        setFile(null)
        return
      }
      setFile(selectedFile)
      setError('')
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    if (!consent) {
      setError('Please consent to behavioural analysis')
      return
    }

    setUploading(true)
    setError('')

    const formData = new FormData()
    formData.append('file', file)
    formData.append('consent_given', 'true')

    try {
      await axios.post('/api/behaviour/upload-linkedin', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setSuccess(true)
      setTimeout(() => {
        navigate('/applicant/dashboard')
      }, 2000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">Upload LinkedIn Profile</h1>
        </div>

        <div className="p-6">
          {/* Info Banner */}
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start">
              <Info className="h-5 w-5 text-blue-600 mt-0.5 mr-2 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-medium text-blue-900">How to export your LinkedIn profile</h3>
                <ol className="text-xs text-blue-800 mt-2 space-y-1 list-decimal list-inside">
                  <li>Go to your LinkedIn profile</li>
                  <li>Click "More" → "Save to PDF"</li>
                  <li>Upload the exported PDF here</li>
                </ol>
              </div>
            </div>
          </div>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded flex items-center">
              <AlertCircle className="h-5 w-5 mr-2" />
              {error}
            </div>
          )}

          {success && (
            <div className="mb-4 bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded flex items-center">
              <CheckCircle className="h-5 w-5 mr-2" />
              LinkedIn profile uploaded successfully! Redirecting...
            </div>
          )}

          <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-primary-400 transition-colors">
            <input
              type="file"
              id="linkedin-upload"
              className="hidden"
              accept=".pdf"
              onChange={handleFileChange}
              disabled={uploading}
            />
            <label htmlFor="linkedin-upload" className="cursor-pointer">
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-sm text-gray-600">
                Click to upload your LinkedIn PDF export
              </p>
              <p className="text-xs text-gray-500 mt-1">
                PDF only (max 5MB)
              </p>
            </label>
          </div>

          {file && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg flex items-center">
              <FileText className="h-5 w-5 text-gray-500 mr-3" />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{file.name}</p>
                <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
              </div>
              <button
                onClick={() => setFile(null)}
                className="text-red-600 hover:text-red-700 text-sm"
              >
                Remove
              </button>
            </div>
          )}

          {/* Consent Checkbox */}
          <div className="mt-6">
            <label className="flex items-start">
              <input
                type="checkbox"
                checked={consent}
                onChange={(e) => setConsent(e.target.checked)}
                className="mt-1 h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <span className="ml-2 text-sm text-gray-700">
                I consent to behavioural analysis of my LinkedIn profile text to infer approximate Big Five personality traits (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism). I understand this is an approximate, non-clinical indicator and will be used for recruitment purposes only.
              </span>
            </label>
          </div>

          <div className="mt-6">
            <button
              onClick={handleUpload}
              disabled={!file || !consent || uploading}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? 'Uploading and analyzing...' : 'Upload LinkedIn Profile'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
