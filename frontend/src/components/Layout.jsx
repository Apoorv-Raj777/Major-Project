import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Briefcase, User, LogOut, FileText, BarChart3, Upload, Menu, X } from 'lucide-react'
import { useState } from 'react'

export default function Layout() {
  const { user, logout, isRecruiter, isApplicant, loading } = useAuth()
  const navigate = useNavigate()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-2 border-gray-300 border-t-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Briefcase className="h-8 w-8 text-primary-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">
                Resume Screening
              </span>
            </div>
            
            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-4">
              {isRecruiter && (
                <>
                  <Link to="/dashboard" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md hover:bg-gray-50 transition-colors">
                    Dashboard
                  </Link>
                  <Link to="/jobs/create" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md hover:bg-gray-50 transition-colors">
                    Post Job
                  </Link>
                  <Link to="/fairness" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md hover:bg-gray-50 transition-colors">
                    Fairness
                  </Link>
                </>
              )}
              
              {isApplicant && (
                <>
                  <Link to="/applicant/dashboard" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md hover:bg-gray-50 transition-colors">
                    Dashboard
                  </Link>
                  <Link to="/applicant/upload-resume" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md hover:bg-gray-50 transition-colors">
                    Upload Resume
                  </Link>
                  <Link to="/applicant/my-scores" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md hover:bg-gray-50 transition-colors">
                    My Scores
                  </Link>
                </>
              )}
              
              <div className="flex items-center space-x-3 ml-4 pl-4 border-l border-gray-200">
                <User className="h-5 w-5 text-gray-500" />
                <span className="text-sm text-gray-700 hidden lg:block">{user?.full_name || user?.email}</span>
                <button
                  onClick={handleLogout}
                  className="p-2 text-gray-500 hover:text-red-600 transition-colors rounded-md hover:bg-gray-50"
                  title="Logout"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </div>
            </nav>

            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-gray-500 hover:text-gray-700"
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 bg-white">
            <div className="px-4 py-3 space-y-2">
              {isRecruiter && (
                <>
                  <Link
                    to="/dashboard"
                    className="block text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md hover:bg-gray-50"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/jobs/create"
                    className="block text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md hover:bg-gray-50"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Post Job
                  </Link>
                  <Link
                    to="/fairness"
                    className="block text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md hover:bg-gray-50"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Fairness
                  </Link>
                </>
              )}
              
              {isApplicant && (
                <>
                  <Link
                    to="/applicant/dashboard"
                    className="block text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md hover:bg-gray-50"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/applicant/upload-resume"
                    className="block text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md hover:bg-gray-50"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Upload Resume
                  </Link>
                  <Link
                    to="/applicant/my-scores"
                    className="block text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md hover:bg-gray-50"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    My Scores
                  </Link>
                </>
              )}
              
              <div className="pt-2 border-t border-gray-200">
                <div className="flex items-center space-x-2 px-3 py-2">
                  <User className="h-5 w-5 text-gray-500" />
                  <span className="text-sm text-gray-700">{user?.full_name || user?.email}</span>
                </div>
                <button
                  onClick={() => {
                    handleLogout()
                    setMobileMenuOpen(false)
                  }}
                  className="w-full text-left text-gray-700 hover:text-red-600 px-3 py-2 rounded-md hover:bg-gray-50 flex items-center"
                >
                  <LogOut className="h-5 w-5 mr-2" />
                  Logout
                </button>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  )
}
