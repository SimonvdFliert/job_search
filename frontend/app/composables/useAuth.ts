interface LoginResponse {
  access_token: string
  token_type: string
}

interface User {
  id: number
  username: string
  email: string
  full_name: string
  permissions: {
    can_scrape: boolean
    can_view_analytics: boolean
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

  // Login
  const login = async (identifier: string, password: string, remember: boolean = false) => {
    const formData = new URLSearchParams()
    formData.append('username', identifier)
    formData.append('password', password)

    const { data, error } = await useFetch<LoginResponse>(`${apiBase}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    })

    if (error.value) {
      throw new Error(error.value.data?.detail || 'Login failed')
    }

    if (data.value) {
      console.log('data value', data.value)
      // Store token
      token.value = data.value.access_token
      
      if (process.client) {
        const storage = remember ? localStorage : sessionStorage
        storage.setItem('access_token', data.value.access_token)
        storage.setItem('token_type', data.value.token_type)
      }
      
      // Fetch user data
      await fetchUser()
      
      return data.value
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
    token.value = null
    user.value = null

    if (process.client) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('token_type')
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('token_type')
    }

    await navigateTo('/login')
  }

  // Fetch current user
  const fetchUser = async () => {
    if (!token.value) return null

    try {
      const { data, error } = await useFetch<User>(`${apiBase}/auth/me`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      })

      if (error.value) {
        // Token invalid, clear it
        await logout()
        return null
      }

      user.value = data.value
      return data.value
    } catch (err) {
      await logout()
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
  }
}