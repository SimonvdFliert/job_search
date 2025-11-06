<template>
  <div class="auth-callback">
    <p v-if="isLoading">Completing login...</p>
    <p v-if="error">Login failed: {{ error }}</p>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const { setToken } = useAuth() // You'll need to add this to your auth composable
const isLoading = ref(true)
const error = ref('')

onMounted(async () => {
  const token = route.query.token as string
  const authError = route.query.error as string

  if (authError) {
    error.value = authError
    isLoading.value = false
    setTimeout(() => {
      router.push('/login')
    }, 3000)
    return
  }

  if (token) {
    // Store the token (same as traditional login)
    setToken(token)
    
    // Redirect to dashboard or home
    await router.push('/')
  } else {
    error.value = 'No token received'
    isLoading.value = false
  }
})
</script>