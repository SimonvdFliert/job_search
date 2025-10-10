<script lang="ts" setup>
  const colorMode = useColorMode();
  const { user, isAuthenticated, canScrape, logout } = useAuth()

  console.log('USER IN NVABAR', user.value)
  console.log('isAuthenticated', isAuthenticated.value)


  const toggleTheme = () => {
    // Cycle through 'light', 'dark', and 'system'
    const values = ['light', 'dark'];
    const currentValue = colorMode.preference;
    console.log('Current color mode:', currentValue);
    const nextValue = values[(values.indexOf(currentValue) + 1) % values.length];
    colorMode.preference = nextValue;
  }


  const showUserMenu = ref(false)
  const userMenuRef = ref<HTMLElement | null>(null)

  const toggleUserMenu = () => {
    showUserMenu.value = !showUserMenu.value
  }

  const handleLogout = async () => {
    showUserMenu.value = false
    await logout()
  }

  // Close dropdown when clicking outside
  onMounted(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.value && !userMenuRef.value.contains(event.target as Node)) {
        showUserMenu.value = false
      }
    }
    
    document.addEventListener('click', handleClickOutside)
    
    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
    })
  })

</script>

<template>
    <!-- bg-white border-gray-200 dark:bg-gray-800-->
<nav class="bg-navbar">
  <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
    
    <NuxtLink to="/" class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white">
      JobSearch
    </NuxtLink>

    <button data-collapse-toggle="navbar-default" type="button" class="inline-flex items-center p-2 w-10 h-10 justify-center text-sm rounded-lg md:hidden focus:outline-none focus:ring-2" aria-controls="navbar-default" aria-expanded="false">
      <span class="sr-only">Open main menu</span>
      <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 17 14">
        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h15M1 7h15M1 13h15"/>
      </svg>
    </button>
    
    <div class="hidden w-full md:block md:w-auto" id="navbar-default">
      <div class="flex items-center gap-8">
        <NuxtLink to="/" class="py-2 px-3 rounded-sm md:bg-transparent text-navbar-text hover:text-navbar-hover md:p-0">
          Job Finder
        </NuxtLink>
        <NuxtLink to="/statistics" class="py-2 px-3 rounded-sm md:bg-transparent text-navbar-text hover:text-navbar-hover md:p-0">
          Statistics
        </NuxtLink>
          <template v-if="isAuthenticated">

            <!-- Admin-only link -->
            <NuxtLink 
              v-if="canScrape"
              to="/admin" 
              class="py-2 px-3 rounded-sm md:bg-transparent text-navbar-text hover:text-navbar-hover md:p-0"
            >
              Admin
            </NuxtLink>

            <!-- User menu -->
            <div class="relative" ref="userMenuRef">
              <button 
                @click="toggleUserMenu"
                class="flex items-center space-x-2 py-2 px-3 rounded-sm md:bg-transparent text-navbar-text hover:text-navbar-hover md:p-0"
              >
                {{ user?.username }}
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <!-- Dropdown menu -->
              <div 
                v-if="showUserMenu"
                class="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5"
              >
                <div class="py-1">
                  <NuxtLink 
                    to="/profile" 
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                    @click="showUserMenu = false"
                  >
                    Your Profile
                  </NuxtLink>
                  <NuxtLink 
                    to="/settings" 
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                    @click="showUserMenu = false"
                  >
                    Settings
                  </NuxtLink>
                  <button 
                    @click="handleLogout"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                  >
                    Sign out
                  </button>
                </div>
              </div>
            </div>
          </template>

          <!-- Guest links -->
          <template v-else>
            <NuxtLink 
              to="/login" 
              class="flex items-center space-x-2 py-2 px-3 rounded-sm md:bg-transparent text-navbar-text hover:text-navbar-hover md:p-0"
            >
              Login
            </NuxtLink>
            <NuxtLink 
              to="/signup" 
              class="flex items-center space-x-2 py-2 px-3 rounded-sm md:bg-transparent text-navbar-text hover:text-navbar-hover md:p-0"
            >
              Sign up
            </NuxtLink>
          </template>
      </div>
    </div>
    
    <button @click="toggleTheme" type="button" class="text-navbar-text focus:outline-none focus:ring-4 rounded-lg text-sm p-2.5">
    
    <svg v-if="colorMode.value === 'light'" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
        <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path>
    </svg>

    <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
        <path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" fill-rule="evenodd" clip-rule="evenodd"></path>
    </svg>
    </button>
    
  </div>
</nav>

    
</template>

<style scoped>

</style>