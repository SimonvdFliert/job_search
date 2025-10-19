<template>
  <section class="bg-gray-50 dark:bg-gray-900">
    <div class="flex flex-col items-center justify-center px-6 py-8 mx-auto md:h-screen">
      <div class="w-full bg-white rounded-lg shadow dark:border md:mt-0 sm:max-w-md xl:p-0 dark:bg-gray-800">
        <div class="p-6 space-y-4 md:space-y-6 sm:p-8">
          <h1 class="text-xl font-bold text-gray-900 md:text-2xl dark:text-white">
            Sign in to your account
          </h1>
          
          <div v-if="errorMessage" class="p-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400">
            {{ errorMessage }}
          </div>
          
          <form @submit.prevent="handleLogin" class="space-y-4">
            <div>
              <label for="identifier" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                Email or Username
              </label>
              <input 
                v-model="identifier" 
                type="text" 
                id="identifier" 
                class="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:text-white" 
                required
                :disabled="loading"
              >
            </div>
            
            <div>
              <label for="password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                Password
              </label>
              <input 
                v-model="password" 
                type="password" 
                id="password" 
                class="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:text-white" 
                required
                :disabled="loading"
              >
            </div>
            
            <div class="flex items-center justify-between">
              <div class="flex items-start">
                <input v-model="rememberMe" id="remember" type="checkbox" class="w-4 h-4">
                <label for="remember" class="ml-2 text-sm text-gray-500 dark:text-gray-300">
                  Remember me
                </label>
              </div>
              <NuxtLink to="/forgot-password" class="text-sm text-card-text hover:underline">
                Forgot password?
              </NuxtLink>
            </div>
            
            <button 
              type="submit" 
              :disabled="loading"
              class="w-full text-card-text font-bold py-3 px-6 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap bg-button-primary hover:bg-button-primary-hover"
            >
              {{ loading ? 'Signing in...' : 'Sign in' }}
            </button>
            
            <p class="text-sm text-gray-500 dark:text-gray-400">
              Don't have an account? 
              <NuxtLink to="/signup" class="text-primary-600 hover:underline">
                Sign up
              </NuxtLink>
            </p>
          </form>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const { login, clearAuthState } = useAuth()
const { success, error } = useToast()

const identifier = ref('')
const password = ref('')
const rememberMe = ref(false)
const errorMessage = ref('')
const loading = ref(false)

onMounted(() => {
  clearAuthState()
})


const handleLogin = async () => {
  errorMessage.value = ''
  loading.value = true

  try {
    await login(identifier.value, password.value, rememberMe.value)
    await navigateTo('/')
    success('Logged in successfully!')
  } catch (err: any) {
    errorMessage.value = err.message || 'Login failed'
    error('Login failed. Please try again.')
  } finally {
    loading.value = false
  }
}
</script>