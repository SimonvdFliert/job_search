<template>
  
  <div class="min-h-screen font-sans ">
    <div class="container mx-auto px-4">
      <h1 class="text-4xl font-bold mb-2 mt-5 text-card-text">Job Search</h1>
      <p class="text-card-text mb-8">
        Enter a query to find jobs using semantic search.
      </p>

      <!-- Search Form -->
      <form @submit.prevent="searchJobs" class="flex items-center gap-4 mb-8">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="e.g., Senior Python Engineer in Amsterdam"
          class="w-full rounded-lg px-4 py-3 focus:outline-none transition-colors"
        />
        <button
          type="submit"
          @click="handleSearch"
          :disabled="!searchQuery || isLoading"
          class=" text-card-text  font-bold py-3 px-6 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap bg-button-primary hover:bg-button-primary-hover"
        >
          {{ isLoading ? "Searching..." : "Search" }}
        </button>
      </form>

      <!-- Pagination Controls -->
      <div v-if="totalJobs > 0" class="text-sm text-gray-600">
        Showing {{ (currentPage - 1) * pageSize + 1 }} - 
        {{ Math.min(currentPage * pageSize, totalJobs) }} of {{ totalJobs }} results
      </div>

      <!-- Loading Spinner -->
       <div v-if="isLoading" class="flex justify-center items-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 "></div>
      </div>

      <!-- Results Area -->
      <div v-if="jobs && jobs.length > 0">
        <h2 class="text-2xl font-semibold mb-4">
          Search Results ({{ jobs.length }})
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- Loop through each result and display it as a card -->
          <div v-for="job in jobs"
              :key="job.id"
              class=" rounded-lg p-5 flex flex-col transition-colors bg-card hover:bg-card-hover">
            <div class="flex-grow">
              <h3 class="text-xl font-bold text-card-header">{{ job.title }}</h3>
              <p class="font-semibold mb-2 text-card-text">{{ job.company }}</p>
              <!-- <p class="text-gray-500 text-sm mb-4">{{ job.locations ? JSON.parse(job.locations).join(', ') : 'Location not specified' }}</p> -->
            </div>
            <div class="mt-auto flex justify-between items-center">
               <a :href="job.url" target="_blank" class=" hover:underline text-card-text">View Job &rarr;</a>
               <span class="text-xs font-mono px-2 py-1 rounded text-card-text">
                {{ (job.cosine_sim * 100).toFixed(1) }}%
               </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <nav v-if="totalPages > 1" class="flex justify-center mt-8 mb-8">
        <ul class="inline-flex -space-x-px text-sm">
          <!-- Previous Button -->
          <li>
            <button
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage === 1"
              class="flex items-center justify-center px-3 h-8 ms-0 leading-tight  rounded-s-lg disabled:opacity-50 disabled:cursor-not-allowed text-card-text bg-button-primary hover:bg-button-primary-hover"
            >
              Previous
            </button>
          </li>
          
          <!-- Page Numbers with Ellipsis -->
          <template v-for="(page, index) in getPageNumbers" :key="`page-${page}-${index}`">
            <!-- Ellipsis -->
            <li v-if="shouldShowEllipsisBefore(page, index)">
              <span class="flex items-center justify-center px-3 h-8 leading-tight text-card-text bg-pagination-bg hover:bg-button-primary-hover">
                ...
              </span>
            </li>
            
            <!-- Page Button -->
            <li>
              <button
                @click="goToPage(page)"
                :class="[
                  'flex items-center justify-center px-3 h-8 leading-tight',
                  currentPage === page
                    ? 'text-card-text bg-button-primary hover:bg-button-primary-hover'
                    : 'text-card-text bg-pagination-bg hover:bg-button-primary-hover'
                ]"
              >
                {{ page }}
              </button>
            </li>
          </template>
          
          <!-- Next Button -->
          <li>
            <button
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="flex items-center justify-center px-3 h-8 leading-tight rounded-e-lg text-card-text bg-button-primary hover:bg-button-primary-hover disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </li>
        </ul>
      </nav>

       <!-- Error Message -->
      <div v-if="error" class="mt-4">
        <div class="bg-red-900 border border-red-700 text-red-200 p-4 rounded-lg">
          <p class="font-bold">An error occurred:</p>
          <p>{{ error }}</p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
const { public: { apiBase } } = useRuntimeConfig()
const { user, fetchUser } = useAuth()

definePageMeta({
  middleware: 'auth'
})
// Ensure we have fresh user data
onMounted(async () => {
  if (!user.value) {
    await fetchUser()
  }
})

interface Job {
  id: string;
  title: string;
  company: string;
  locations: string[];
  posted_at: string;
  url: string;
  cosine_sim: number;
}

interface PaginatedResponse {
  items: Job[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

const searchQuery = ref('');
const currentPage = ref(1);
const pageSize = ref(50);
const jobs = ref<Job[]>([]);
const totalPages = ref(0);
const totalJobs = ref(0);
const isLoading = ref(false);
const error = ref<string | null>(null);



const getPageNumbers = computed(() => {
  const pages = [];
  const total = totalPages.value;
  const current = currentPage.value;
  
  // Always show first page
  pages.push(1);
  
  // Show pages around current page
  for (let i = Math.max(2, current - 2); i <= Math.min(total - 1, current + 2); i++) {
    pages.push(i);
  }
  
  // Always show last page
  if (total > 1) {
    pages.push(total);
  }
  
  // Remove duplicates and sort
  return [...new Set(pages)].sort((a, b) => a - b);
});

const shouldShowEllipsisBefore = (page: number, index: number) => {
  const pages = getPageNumbers.value;
  return index > 0 && page - pages[index - 1] > 1;
};


const searchJobs = async () => {
  if (!searchQuery.value.trim()) {
    jobs.value = [];
    return;
  }

  isLoading.value = true;
  jobs.value = [];
  error.value = null;

  try {
    const response  = await fetch(
      `${apiBase}/search?q=${encodeURIComponent(searchQuery.value)}&page=${currentPage.value}&page_size=${pageSize.value}`,
    );
    
    if (!response.ok) {
      throw new Error('Search failed');
    }
    
    const data: PaginatedResponse = await response.json();
    
    console.log('API Response:', data); // Debug: check what you're getting
    jobs.value = data.items;
    totalPages.value = data.total_pages;
    totalJobs.value = data.total;

  } catch (error) {
    console.error('Search failed:', error);
    jobs.value = [];
  } finally {
    isLoading.value = false;
  }
};

// Watch for page changes
watch(currentPage, () => {
  if (searchQuery.value) {
    searchJobs();
  }
});

const handleSearch = () => {
  currentPage.value = 1; // Reset to page 1 on new search
  searchJobs();
};

const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};
</script>

<style>
</style>
