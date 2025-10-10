export default defineNuxtPlugin(async () => {
  const { fetchUser, token } = useAuth()
  
  // If there's a token on app start, fetch the user
  if (token.value) {
    await fetchUser()
  }
})