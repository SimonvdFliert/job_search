interface LoginResponse {
  access_token: string
  token_type: string
}

interface User {
  // id: number
  // username: string
  // email: string
  // full_name: string
  is_superuser: boolean
  permissions: {
    can_scrape: boolean
    // can_view_analytics: boolean
    [key: string]: boolean
  }
}

interface SignupData {
  username: string
  email: string
  full_name: string
  password: string
}

export const useAuth = () => {
  const { public: { apiBase } } = useRuntimeConfig()

  // Reactive state
  const token = useState<string | null>('auth_token', () => {
    // Initialize from storage on client side
    if (process.client) {
      return localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
    }
    return null
  })
  
  const user = useState<User | null>('user', () => null)
  console.log('user', user)
    // Clear all auth state
  const clearAuthState = () => {
    console.log('🧹 Clearing auth state...')
    token.value = null
    user.value = null

    if (process.client) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('token_type')
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('token_type')
    }
    console.log('✅ Auth state cleared')
  }



  // Login
  const login = async (identifier: string, password: string, remember: boolean = false) => {
    console.log('🔐 Starting login for:', identifier) 
    clearAuthState()

    try {
      const formData = new URLSearchParams()
      formData.append('username', identifier)
      formData.append('password', password)

      // Use $fetch instead of useFetch to avoid caching
      const data = await $fetch<LoginResponse>(`${apiBase}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      })

      console.log('✅ Login response received')

      // Store token
      token.value = data.access_token
      
      if (process.client) {
        const storage = remember ? localStorage : sessionStorage
        storage.setItem('access_token', data.access_token)
        storage.setItem('token_type', data.token_type)
      }
      
      // Fetch fresh user data for this token
      await fetchUser()
      
      console.log('✅ Login complete, user:', user.value)
      
      return data
    } catch (error: any) {
      console.error('❌ Login failed:', error)
      throw new Error(error.data?.detail || 'Login failed')
    }

  }
  // Signup
  const signup = async (signupData: SignupData) => {
    const { data, error } = await useFetch(`${apiBase}/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(signupData),
    })

    if (error.value) {
      throw new Error(error.value.data?.detail || 'Signup failed')
    }

    return data.value
  }

  // Logout
  const logout = async () => {
    console.log('👋 Logging out...')
    clearAuthState()
    if (process.client) {
          window.location.href = '/login'
    } else {
          await navigateTo('/login')
        }
  }

  // Fetch current user
  const fetchUser = async () => {
    if (!token.value) {
          console.log('⚠️ No token, skipping user fetch')
          user.value = null
          return null
        }

    try {
      // Use $fetch to avoid any caching issues
      const data = await $fetch<User>(`${apiBase}/auth/me`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      })
      user.value = data
      return data
    } catch (error: any) {
      console.error('Failed to fetch user:', error)
      // Token is invalid, clear everything
      clearAuthState()
      return null
    }
  }

  // Get auth header for API calls
  const getAuthHeader = () => {
    if (!token.value) return {}
    return {
      Authorization: `Bearer ${token.value}`,
    }
  }

  // Computed properties
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const canScrape = computed(() => user.value?.permissions?.can_scrape ?? false)
  const canViewAnalytics = computed(() => user.value?.permissions?.can_view_analytics ?? false)

  return {
    token,
    user,
    login,
    signup,
    logout,
    fetchUser,
    getAuthHeader,
    isAuthenticated,
    canScrape,
    canViewAnalytics,
    clearAuthState,
  }
}