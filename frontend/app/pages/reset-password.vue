<template>
    <section class="bg-gray-50 dark:bg-gray-900">
        <div class="flex flex-col items-center justify-center px-6 py-8 mx-auto md:h-screen lg:py-0">
            <a href="#" class="flex items-center mb-6 text-2xl font-semibold text-gray-900 dark:text-white">
                <img class="w-8 h-8 mr-2" src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/logo.svg" alt="logo">
                Flowbite    
            </a>
            <div class="w-full p-6 bg-white rounded-lg shadow dark:border md:mt-0 sm:max-w-md dark:bg-gray-800 dark:border-gray-700 sm:p-8">
                <h1 class="mb-1 text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl dark:text-white">
                    Change Password
                </h1>
                 <div v-if="!token">
                    <p class="p-4 mt-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400">No reset token provided</p>
                </div>
                    
                <div v-else>
                    <form @submit.prevent="resetPassword">
                        <div class="mt-4 space-y-4 lg:mt-5 md:space-y-5">
                        <label for="password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">New Password</label>
                        <input
                            id="password"
                            v-model="newPassword"
                            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white" 
                            type="password"
                            required
                            minlength="8"
                            placeholder="Enter new password"
                        />
                        </div>
                        
                        <div class="mt-4 space-y-4 lg:mt-5 md:space-y-5">
                        <label for="confirmPassword" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Confirm Password</label>
                        <input
                            id="confirmPassword"
                            v-model="confirmPassword"
                            type="password"
                            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white" 
                            required
                            placeholder="Confirm new password"
                        />
                        </div>
                        
                        <p v-if="error" class="error">{{ error }}</p>
                        <p v-if="success" class="success">{{ success }}</p>
                        
                        <button type="submit" :disabled="loading"
                        class="w-full font-medium text-primary-600 hover:underline dark:text-primary-500">
                        {{ loading ? 'Resetting...' : 'Reset Password' }}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </section>
</template>

<script setup>
const route = useRoute()
const { public: { apiBase } } = useRuntimeConfig()

const token = ref(route.query.token)
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

const resetPassword = async () => {
  error.value = ''
  success.value = ''
  
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }
  
  if (newPassword.value.length < 8) {
    error.value = 'Password must be at least 8 characters'
    return
  }
  
  loading.value = true
  
  try {
    await $fetch(`${apiBase}/auth/reset_password`, {
      method: 'POST',
      body: {
        token: token.value,
        new_password: newPassword.value
      }
    })
    
    success.value = 'Password reset successfully! Redirecting to login...'
    
    setTimeout(() => {
      navigateTo('/login')
    }, 2000)
  } catch (err) {
    error.value = err.data?.detail || 'Failed to reset password. Token may be invalid or expired.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>

</style>