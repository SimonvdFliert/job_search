interface LoginResponse {
  access_token: string
  token_type: string
}

interface User {
  // id: number
  username: string
  email: string
  full_name: string
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
  const { success, error } = useToast()
  // Reactive state
  const token = useState<string | null>('auth_token', () => {
    // Initialize from storage on client side
    if (process.client) {
      return localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
    }
    return null
  })
  
  const user = useState<User | null>('user', () => null)
    // Clear all auth state
  const clearAuthState = () => {
    token.value = null
    user.value = null

    if (process.client) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('token_type')
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('token_type')
    }
  }



  // Login
  const login = async (identifier: string, password: string, remember: boolean = false) => {
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

      // Store token
      token.value = data.access_token
      
      if (process.client) {
        const storage = remember ? localStorage : sessionStorage
        storage.setItem('access_token', data.access_token)
        storage.setItem('token_type', data.token_type)
      }
      
      // Fetch fresh user data for this token
      await fetchUser()
            
      return data
    } catch (error: any) {
      error('Login Faield')
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
      error('Signup Failed')
      throw new Error(error.value.data?.detail || 'Signup failed')
    }

    return data.value
  }


  const resetPassword = async (passwordData) => {
    console.log('password data in reset Password', passwordData)
    console.log('password data in reset Password value', passwordData.value)

    const password_data = {
      "current": passwordData.value.current,
      "new": passwordData.value.new,
    }

    const { data, error } = await useFetch(`${apiBase}/auth/change_password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token.value}`,
      },
      body: JSON.stringify(password_data),
    })

    if (error.value) {
      error('Password Reset Failed')
      throw new Error(error.value.data?.detail || 'Signup failed')
    }

    return data.value
  }

  const deleteUser = async (deleteModalData) => {
      const password_data = {
        "password": deleteModalData.value.password,
      }
      const { data, error } = await useFetch(`${apiBase}/auth/delete_account`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token.value}`,
        },
        body: JSON.stringify(password_data)
      })

      if (error.value) {
        error('Account Deletion Failed')
        throw new Error(error.value.data?.detail || 'Signup failed')
      }

      return data.value
    }



  // Logout
  const logout = async () => {
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
      // Token is invalid, clear everything
      error('Session Expired. Please log in again.')
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
    resetPassword,
    deleteUser,
    fetchUser,
    getAuthHeader,
    isAuthenticated,
    canScrape,
    canViewAnalytics,
    clearAuthState,
  }
}