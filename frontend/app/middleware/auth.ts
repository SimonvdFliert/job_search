export default defineNuxtRouteMiddleware(async (to, from) => {
  const { user, fetchUser, isAuthenticated, token } = useAuth()

  // If we have a token but no user data, try to fetch it
  if (token.value && !user.value) {
    await fetchUser()
  }

  // If still not authenticated after trying to fetch, redirect to login
  if (!isAuthenticated.value) {
    return navigateTo('/login')
  }
})