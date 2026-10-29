import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import RecruiterDashboard from './pages/recruiter/Dashboard'
import FairnessDashboard from './pages/recruiter/FairnessDashboard'
import ApplicantDashboard from './pages/applicant/Dashboard'
import JobCreate from './pages/recruiter/JobCreate'
import JobDetail from './pages/recruiter/JobDetail'
import ResumeUpload from './pages/applicant/ResumeUpload'
import MyScores from './pages/applicant/MyScores'
import LinkedInUpload from './pages/applicant/LinkedInUpload'
import BehaviourSummary from './pages/applicant/BehaviourSummary'

function ProtectedRoute({ children, allowedRole }) {
  const { isAuthenticated, loading, isRecruiter, isApplicant } = useAuth()
  
  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  if (allowedRole === 'recruiter' && !isRecruiter) {
    return <Navigate to="/applicant/dashboard" replace />
  }
  
  if (allowedRole === 'applicant' && !isApplicant) {
    return <Navigate to="/dashboard" replace />
  }
  
  return children
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            
            {/* Recruiter Routes */}
            <Route 
              path="dashboard" 
              element={
                <ProtectedRoute allowedRole="recruiter">
                  <RecruiterDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="jobs/create" 
              element={
                <ProtectedRoute allowedRole="recruiter">
                  <JobCreate />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="jobs/:id" 
              element={
                <ProtectedRoute allowedRole="recruiter">
                  <JobDetail />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="fairness" 
              element={
                <ProtectedRoute allowedRole="recruiter">
                  <FairnessDashboard />
                </ProtectedRoute>
              } 
            />
            
            {/* Applicant Routes */}
            <Route 
              path="applicant/dashboard" 
              element={
                <ProtectedRoute allowedRole="applicant">
                  <ApplicantDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="applicant/upload-resume" 
              element={
                <ProtectedRoute allowedRole="applicant">
                  <ResumeUpload />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="applicant/my-scores" 
              element={
                <ProtectedRoute allowedRole="applicant">
                  <MyScores />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="applicant/upload-linkedin" 
              element={
                <ProtectedRoute allowedRole="applicant">
                  <LinkedInUpload />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="applicant/behaviour" 
              element={
                <ProtectedRoute allowedRole="applicant">
                  <BehaviourSummary />
                </ProtectedRoute>
              } 
            />
          </Route>
        </Routes>
      </AuthProvider>
    </Router>
  )
}

export default App
