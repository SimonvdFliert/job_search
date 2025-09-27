module.exports = {
  darkMode: 'class',
  content: [
    './components/**/*.{js,vue,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './plugins/**/*.{js,ts}',
    './app.vue',
    './error.vue',
  ],
  theme: {
    extend: {
      colors: {
        // Component-specific backgrounds
        'navbar': {
          'DEFAULT': 'var(--color-navbar-bg)',
          'text': 'var(--color-navbar-text)',
          'hover': 'var(--color-navbar-hover)',
        },
        'card': {
          'DEFAULT': 'var(--color-card-bg)',
          'text': 'var(--color-card-text)',
          'border': 'var(--color-card-border)',
          'header': 'var(--color-card-header)',
          'hover': 'var(--color-card-hover)',
        },
        'sidebar': {
          'DEFAULT': 'var(--color-sidebar-bg)',
          'text': 'var(--color-sidebar-text)',
          'active': 'var(--color-sidebar-active)',
        },
        'button': {
          'primary': 'var(--color-button-primary)',
          'secondary': 'var(--color-button-secondary)',
          'danger': 'var(--color-button-danger)',
          'primary-hover': 'var(--color-button-primary-hover)',
          'secondary-hover': 'var(--color-button-secondary-hover)',
          'danger-hover': 'var(--color-button-danger-hover)',
        },
        // Page sections
        'hero': {
          'DEFAULT': 'var(--color-hero-bg)',
          'text': 'var(--color-hero-text)',
        },
        'footer': {
          'DEFAULT': 'var(--color-footer-bg)',
          'text': 'var(--color-footer-text)',
        },
        // Global colors (still useful for edge cases)
        'page': 'var(--color-page-bg)',
        'accent': 'var(--color-accent)',
      }
    },
  },
  plugins: [
    require('flowbite/plugin')
  ],
}