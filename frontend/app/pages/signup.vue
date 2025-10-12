<template>
  <section class="bg-gray-50 dark:bg-gray-900">
    <div class="flex flex-col items-center justify-center px-6 py-8 mx-auto md:h-screen lg:py-0">
      <NuxtLink to="/" class="flex items-center mb-6 text-2xl font-semibold text-gray-900 dark:text-white">
        <img class="w-8 h-8 mr-2" src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/logo.svg" alt="logo">
        JobSearch    
      </NuxtLink>
      
      <div class="w-full bg-white rounded-lg shadow dark:border md:mt-0 sm:max-w-md xl:p-0 dark:bg-gray-800 dark:border-gray-700">
        <div class="p-6 space-y-4 md:space-y-6 sm:p-8">
          <h1 class="text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl dark:text-white">
            Create an account
          </h1>

          <!-- Error Message -->
          <div v-if="errorMessage" class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400">
            {{ errorMessage }}
          </div>

          <!-- Success Message -->
          <div v-if="successMessage" class="p-4 mb-4 text-sm text-green-800 rounded-lg bg-green-50 dark:bg-gray-800 dark:text-green-400">
            {{ successMessage }}
          </div>
          
          <form class="space-y-4 md:space-y-6" @submit.prevent="handleSignup">
            <div>
              <label for="username" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                Username
              </label>
              <input 
                v-model="formData.username" 
                type="text" 
                id="username" 
                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white" 
                placeholder="johndoe" 
                required
                :disabled="loading"
              >
            </div>

            <div>
              <label for="full_name" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                Full Name
              </label>
              <input 
                v-model="formData.full_name" 
                type="text" 
                id="full_name" 
                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white" 
                placeholder="John Doe" 
                required
                :disabled="loading"
              >
            </div>

            <div>
              <label for="email" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                Your email
              </label>
              <input 
                v-model="formData.email" 
                type="email" 
                id="email" 
                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white" 
                placeholder="name@company.com" 
                required
                :disabled="loading"
              >
            </div>

            <div>
              <label for="password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                Password
              </label>
              <input 
                v-model="formData.password" 
                type="password" 
                id="password" 
                placeholder="••••••••" 
                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white" 
                required
                :disabled="loading"
              >
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Minimum 8 characters
              </p>
            </div>

            <div>
              <label for="confirm-password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                Confirm password
              </label>
              <input 
                v-model="confirmPassword" 
                type="password" 
                id="confirm-password" 
                placeholder="••••••••" 
                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white" 
                required
                :disabled="loading"
              >
            </div>

            <div class="flex items-start">
              <div class="flex items-center h-5">
                <input 
                  v-model="acceptTerms" 
                  id="terms" 
                  type="checkbox" 
                  class="w-4 h-4 border border-gray-300 rounded bg-gray-50 focus:ring-3 focus:ring-primary-300 dark:bg-gray-700 dark:border-gray-600" 
                  required
                >
              </div>
              <div class="ml-3 text-sm">
                <label for="terms" class="font-light text-gray-500 dark:text-gray-300">
                  I accept the 
                  <NuxtLink to="/terms" class="font-medium text-primary-600 hover:underline dark:text-primary-500">
                    Terms and Conditions
                  </NuxtLink>
                </label>
              </div>
            </div>

            <button 
              type="submit" 
              :disabled="loading"
              class="w-full text-card-text font-bold py-3 px-6 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap bg-button-primary hover:bg-button-primary-hover disabled:cursor-not-allowed"
            >
              <span v-if="!loading">Create an account</span>
              <span v-else class="flex items-center justify-center">
                <svg class="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Creating account...
              </span>
            </button>

            <p class="text-sm font-light text-gray-500 dark:text-gray-400">
              Already have an account?
              <NuxtLink to="/login" class="font-medium text-primary-600 hover:underline dark:text-primary-500">
                Login here
              </NuxtLink>
            </p>
          </form>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const { signup } = useAuth()
const { success, error } = useToast()

const formData = reactive({
  username: '',
  email: '',
  full_name: '',
  password: '',
})

const confirmPassword = ref('')
const acceptTerms = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const loading = ref(false)

const handleSignup = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  
  // Client-side validation
  if (!formData.username || !formData.email || !formData.password || !confirmPassword.value || !formData.full_name) {
    errorMessage.value = 'Please fill in all fields.'
    error(errorMessage.value)
    return
  }

  if (formData.username.length < 3) {
    errorMessage.value = 'Username must be at least 3 characters long.'
    error(errorMessage.value)
    return
  }

  if (formData.password.length < 8) {
    errorMessage.value = 'Password must be at least 8 characters long.'
    error(errorMessage.value)
    return
  }

  if (formData.password !== confirmPassword.value) {
    errorMessage.value = 'Passwords do not match.'
    error(errorMessage.value)
    return
  }

  if (!acceptTerms.value) {
    errorMessage.value = 'You must accept the terms and conditions.'
    error(errorMessage.value)
    return
  }

  loading.value = true

  try {
    await signup(formData)
    
    successMessage.value = 'Account created successfully! Redirecting to login...'
    success(successMessage.value)
    // Clear form
    formData.username = ''
    formData.email = ''
    formData.full_name = ''
    formData.password = ''
    confirmPassword.value = ''
    acceptTerms.value = false
    
    // Redirect to login after 2 seconds
    setTimeout(() => {
      navigateTo('/login')
    }, 2000)

  } catch (err: any) {
    errorMessage.value = err.message || 'An error occurred during signup.'
    error(errorMessage.value)
  } finally {
    loading.value = false
  }
}
</script>