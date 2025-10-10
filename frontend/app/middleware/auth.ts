export default defineNuxtRouteMiddleware(async (to, from) => {
  const { user, fetchUser, isAuthenticated } = useAuth()

  // If no user data but we have a token, fetch user
  if (!user.value) {
    await fetchUser()
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated.value) {
    return navigateTo('/login')
  }
})