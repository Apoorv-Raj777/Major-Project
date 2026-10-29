import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchUser = async () => {
    try {
      const response = await axios.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUser(response.data)
    } catch (error) {
      localStorage.removeItem('token')
      setToken(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    
    const response = await axios.post('/api/auth/login', formData)
    const { access_token } = response.data
    localStorage.setItem('token', access_token)
    setToken(access_token)
    await fetchUser()
    return response.data
  }

  const checkAuthAndRedirect = () => {
    if (!loading && isAuthenticated) {
      if (isRecruiter) {
        return '/dashboard'
      } else {
        return '/applicant/dashboard'
      }
    }
    return '/login'
  }

  const register = async (userData) => {
    const response = await axios.post('/api/auth/register', userData)
    return response.data
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  const value = {
    user,
    loading,
    token,
    login,
    register,
    logout,
    checkAuthAndRedirect,
    isAuthenticated: !!user,
    isRecruiter: user?.role === 'recruiter',
    isApplicant: user?.role === 'applicant'
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
