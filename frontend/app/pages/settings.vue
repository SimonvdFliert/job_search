<template>
  <div class="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">Settings</h1>

    <!-- Profile Information Section -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow mb-6">
      <div class="p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Profile Information</h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Full Name</label>
            <input 
              type="text" 
              v-model="userData.full_name"
              class="bg-input-bg 
                      text-input-text 
                      border border-input-border 
                      placeholder:text-input-placeholder
                      focus:border-input-focus-border 
                      focus:ring-input-focus-ring
                      rounded-lg px-4 py-2.5 w-full"
              readonly
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Email</label>
            <input 
              type="email" 
              v-model="userData.email"
              class="bg-input-bg 
                      text-input-text 
                      border border-input-border 
                      placeholder:text-input-placeholder
                      focus:border-input-focus-border 
                      focus:ring-input-focus-ring
                      rounded-lg px-4 py-2.5 w-full"
              readonly
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Permissions Section -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow mb-6">
      <div class="p-6">
        <h2 class="text-xl font-semibold text-card-text mb-4">Permissions</h2>
        
        <div class="flex flex-wrap gap-2">
          <span 
            v-for="permission in userData.permissions" 
            :key="permission"
            class="bg-button-primary text-card-text text-sm font-medium px-3 py-1 rounded-full "
          >
            {{ permission }}
          </span>
        </div>
      </div>
    </div>

    <!-- Admin Scrape Data Section -->
    <div v-if="isAdmin" class="bg-white dark:bg-gray-800 rounded-lg shadow mb-6">
      <div class="p-6">
        <h2 class="text-xl font-semibold text-card-text mb-4">Data Scraping</h2>
        <p class="text-sm text-card-text mb-4">
          As an admin, you can initiate data scraping operations.
        </p>
        
        <button 
          @click="handleScrapeData"
          :disabled="isScraping"
          class="text-card-text  font-bold py-3 px-6 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap bg-button-primary hover:bg-button-primary-hover"
        >
          <span v-if="!isScraping">Start Data Scrape</span>
          <span v-else>Scraping...</span>
        </button>

        <div v-if="scrapeMessage" class="mt-4 p-4 text-sm rounded-lg" :class="scrapeSuccess ? 'text-green-800 bg-green-50 dark:bg-gray-800 dark:text-green-400' : 'text-red-800 bg-red-50 dark:bg-gray-800 dark:text-red-400'">
          {{ scrapeMessage }}
        </div>
      </div>
    </div>

    <!-- Reset Password Section -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow mb-6">
      <div class="p-6">
        <h2 class="text-xl font-semibold text-card-text mb-4">Reset Password</h2>
        <p class="text-sm text-card-text mb-4">
          Change your password to keep your account secure.
        </p>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Current Password</label>
            <input 
              type="password" 
              v-model="passwordData.current"
              class="bg-input-bg 
                      text-input-text 
                      border border-input-border 
                      placeholder:text-input-placeholder
                      focus:border-input-focus-border 
                      focus:ring-input-focus-ring
                      rounded-lg px-4 py-2.5 w-full"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">New Password</label>
            <input 
              type="password" 
              v-model="passwordData.new"
              class="bg-input-bg 
                      text-input-text 
                      border border-input-border 
                      placeholder:text-input-placeholder
                      focus:border-input-focus-border 
                      focus:ring-input-focus-ring
                      rounded-lg px-4 py-2.5 w-full"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Confirm New Password</label>
            <input 
              type="password" 
              v-model="passwordData.confirm"
              class="bg-input-bg 
                      text-input-text 
                      border border-input-border 
                      placeholder:text-input-placeholder
                      focus:border-input-focus-border 
                      focus:ring-input-focus-ring
                      rounded-lg px-4 py-2.5 w-full"
            />
          </div>

          <button 
            @click="handleResetPassword"
            class="text-card-text  font-bold py-3 px-6 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap bg-button-primary hover:bg-button-primary-hover"
          >
            Update Password
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Account Section -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow border-2 border-red-200 dark:border-red-900">
      <div class="p-6">
        <h2 class="text-xl font-semibold text-red-600 dark:text-red-500 mb-4">Danger Zone</h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Once you delete your account, there is no going back. Please be certain.
        </p>
        
        <button 
          @click="showDeleteModal = true"
          class="text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 dark:bg-red-600 dark:hover:bg-red-700 focus:outline-none dark:focus:ring-red-800"
        >
          Delete Account
        </button>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 bg-opacity-50">
      <div class="relative p-4 w-full max-w-md">
        <div class="relative bg-white rounded-lg shadow dark:bg-gray-700">
          <button 
            @click="showDeleteModal = false"
            type="button" 
            class="absolute top-3 right-2.5 text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ml-auto inline-flex justify-center items-center dark:hover:bg-gray-600 dark:hover:text-white"
          >
            <svg class="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
              <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
            </svg>
            <span class="sr-only">Close modal</span>
          </button>
          <div class="p-6 text-center">
            <svg class="mx-auto mb-4 text-gray-400 w-12 h-12 dark:text-gray-200" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
              <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 11V6m0 8h.01M19 10a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
            </svg>
            <h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">Are you sure you want to delete your account?</h3>
            <div class="space-y-4 m-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Password</label>
                <input 
                  type="password" 
                  v-model="deleteModalData.password"
                  class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Confirm Password</label>
                <input 
                  type="password" 
                  v-model="deleteModalData.confirmation"
                  class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
                />
              </div>
            </div>
            <button 
              @click="handleDeleteAccount"
              type="button" 
              class="text-white bg-red-600 hover:bg-red-800 focus:ring-4 focus:outline-none focus:ring-red-300 dark:focus:ring-red-800 font-medium rounded-lg text-sm inline-flex items-center px-5 py-2.5 text-center mr-2"
            >
              Yes, I'm sure
            </button>
            <button 
              @click="showDeleteModal = false"
              type="button" 
              class="text-gray-500 bg-white hover:bg-gray-100 focus:ring-4 focus:outline-none focus:ring-gray-200 rounded-lg border border-gray-200 text-sm font-medium px-5 py-2.5 hover:text-gray-900 focus:z-10 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-500 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-600"
            >
              No, cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

definePageMeta({
  middleware: 'auth'
});

const { user, fetchUser, resetPassword, deleteUser, logout, token } = useAuth()
const { public: { apiBase } } = useRuntimeConfig()

onMounted(async () => {
  if (!user.value) {
    await fetchUser()
  }
})


const full_name = user.value?.full_name ?? "Not Found"
const email = user.value?.email ?? "Not Found"
const role = user.value?.permissions
const permissionKeys = Object.entries(user.value?.permissions || {})
            .filter(([key, value]) => value === true)
            .map(([key]) => key);

const userData = {
    "full_name": full_name,
    "email": email,
    "permissions": permissionKeys
}

const isAdmin = computed(() => role?.can_scrape === true)
const passwordData = ref({
  current: '',
  new: '',
  confirm: ''
})

const deleteModalData = ref({
  password: '',
  confirmation: ''
})

const handleResetPassword = async () => {
  if (passwordData.value.new !== passwordData.value.confirm) {
    alert('New passwords do not match!')
    return
  }
  
  // Add your password reset API call here
  console.log('Resetting password...')
  await resetPassword(passwordData)
  alert('Password reset successfully!')

  // Clear form
  passwordData.value = {
    current: '',
    new: '',
    confirm: ''
  }
}

// Delete account
const showDeleteModal = ref(false)

const handleDeleteAccount = async () => {
  if (deleteModalData.value.password !== deleteModalData.value.confirmation) {
    alert('New passwords do not match!')
    return
  }
  // Add your delete account API call here
  console.log('Deleting account...')
  deleteUser(deleteModalData)
  logout()
  alert('Account deleted!')
  showDeleteModal.value = false
  
  // Redirect to login or home page
  navigateTo('/login')
}

// Data scraping (admin only)
const isScraping = ref(false)
const scrapeMessage = ref('')
const scrapeSuccess = ref(false)

const handleScrapeData = async () => {
  isScraping.value = true
  scrapeMessage.value = ''

  try {
      // Use $fetch to avoid any caching issues
      const data = await $fetch(`${apiBase}/data/external_retrieval`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      })
      scrapeMessage.value = 'Data scraping completed successfully!'
      scrapeSuccess.value = true
    }
  catch (error) {
    scrapeMessage.value = 'Failed to scrape data. Please try again.'
    scrapeSuccess.value = false
  } finally {
    isScraping.value = false
  }
}
</script>