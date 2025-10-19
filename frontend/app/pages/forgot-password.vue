<template>
  <section class="bg-gray-50 dark:bg-gray-900">
    <div class="flex flex-col items-center justify-center px-6 py-8 mx-auto md:h-screen lg:py-0">
      <NuxtLink to="/" class="flex items-center mb-6 text-2xl font-semibold text-gray-900 dark:text-white">
        <img class="w-8 h-8 mr-2" src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/logo.svg" alt="logo">
        JobSearch    
      </NuxtLink>
      
      <div class="w-full p-6 bg-white rounded-lg shadow dark:border md:mt-0 sm:max-w-md dark:bg-gray-800 dark:border-gray-700 sm:p-8">
        <h1 class="mb-1 text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl dark:text-white">
          Forgot your password?
        </h1>
        <p class="font-light text-gray-500 dark:text-gray-400">
          Don't worry! Just enter your email and we'll send you a link to reset your password.
        </p>

        <!-- Error Message -->
        <div v-if="errorMessage" class="p-4 mt-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400">
          {{ errorMessage }}
        </div>

        <!-- Success Message -->
        <div v-if="successMessage" class="p-4 mt-4 text-sm text-green-800 rounded-lg bg-green-50 dark:bg-gray-800 dark:text-green-400">
          {{ successMessage }}
        </div>
        
        <form class="mt-4 space-y-4 lg:mt-5 md:space-y-5" @submit.prevent="handleForgotPassword">
          <div>
            <label for="email" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
              Your email
            </label>
            <input 
              v-model="email" 
              type="email" 
              id="email" 
              class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white" 
              placeholder="name@company.com" 
              required
              :disabled="loading"
            >
          </div>

          <button 
            type="submit" 
            :disabled="loading"
            class="w-full text-white bg-primary-600 hover:bg-primary-700 focus:ring-4 focus:outline-none focus:ring-primary-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="!loading">Send reset link</span>
            <span v-else class="flex items-center justify-center">
              <svg class="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Sending...
            </span>
          </button>

          <p class="text-sm font-light text-gray-500 dark:text-gray-400">
            Remember your password? 
            <NuxtLink to="/login" class="font-medium text-primary-600 hover:underline dark:text-primary-500">
              Back to login
            </NuxtLink>
          </p>
        </form>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const { public: { apiBase } } = useRuntimeConfig()
const email = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const loading = ref(false)

const handleForgotPassword = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  
  if (!email.value) {
    errorMessage.value = 'Please enter your email address.'
    return
  }

  loading.value = true

  try {
    await $fetch(`${apiBase}/auth/forgot_password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: email.value,
      }),
    })

    successMessage.value = 'If an account exists with this email, you will receive a password reset link shortly.'
    email.value = '' // Clear form

  } catch (err: any) {
    errorMessage.value = 'An error occurred. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>