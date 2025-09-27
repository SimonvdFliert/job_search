// plugins/flowbite.client.ts
import { onMounted } from 'vue'
import { initFlowbite } from 'flowbite'

export default defineNuxtPlugin((nuxtApp) => {
  // This hook will be called after each page is rendered
  nuxtApp.hook('page:finish', () => {
    initFlowbite();
  });
});