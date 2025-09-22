// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  
  compatibilityDate: '2025-07-15',
  runtimeConfig: {
    public: { apiBase: process.env.API_BASE || 'http://localhost:8000' }
  },
  devtools: { enabled: true },
  css: ['~/assets/css/main.css'],

  vite: {    
    plugins: [      
      tailwindcss(),    
    ],  
  },

  modules: ['nuxt-echarts', '@pinia/nuxt', '@nuxtjs/color-mode'],
  echarts: {
    charts: ['BarChart', 
      'LineChart', 
      'PieChart', 
      'TreemapChart'],
    components: ['DatasetComponent', 
      'GridComponent', 
      'TooltipComponent', 
      'TitleComponent',
      'LegendComponent',],
  },
   colorMode: {
    preference: 'dark', // default value of $colorMode.preference
    fallback: 'light', // fallback value if not system preference found
    hid: 'nuxt-color-mode-script',
    globalName: '__NUXT_COLOR_MODE__',
    componentName: 'ColorScheme',
    classPrefix: '',
    classSuffix: '',
    storage: 'localStorage', // or 'sessionStorage' or 'cookie'
    storageKey: 'nuxt-color-mode'
  }
})