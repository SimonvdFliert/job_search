<template>
  
  <div class="min-h-screen font-sans ">
    <div class="container mx-auto px-4">
      <h1 class="text-4xl font-bold mb-2 mt-5">Job Search</h1>
      <p class=" mb-8">
        Enter a query to find jobs using semantic search.
      </p>

      <!-- Search Form -->
      <form @submit.prevent="searchJobs" class="flex items-center gap-4 mb-8">
        <input
          v-model="query"
          type="text"
          placeholder="e.g., Senior Python Engineer in Amsterdam"
          class="w-full rounded-lg px-4 py-3 focus:outline-none transition-colors"
        />
        <button
          type="submit"
          :disabled="isLoading"
          class=" font-bold py-3 px-6 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap bg-button-primary "
        >
          {{ isLoading ? "Searching..." : "Search" }}
        </button>
      </form>

      <!-- Loading Spinner -->
       <div v-if="isLoading" class="flex justify-center items-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 "></div>
      </div>

      <!-- Results Area -->
      <div v-if="results && results.length > 0">
        <h2 class="text-2xl font-semibold mb-4">
          Search Results ({{ results.length }})
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- Loop through each result and display it as a card -->
          <div v-for="result in results" :key="result.id" class=" rounded-lg p-5 flex flex-col transition-colors bg-card">
            <div class="flex-grow">
              <h3 class="text-xl font-bold text-card-header">{{ result.title }}</h3>
              <p class="font-semibold mb-2 text-card-text">{{ result.company }}</p>
              <!-- <p class="text-gray-500 text-sm mb-4">{{ result.locations ? JSON.parse(result.locations).join(', ') : 'Location not specified' }}</p> -->
            </div>
            <div class="mt-auto flex justify-between items-center">
               <a :href="result.url" target="_blank" class="test-card-text hover:underline">View Job &rarr;</a>
               <span class="text-xs font-mono px-2 py-1 rounded test-card-text">
                {{ (result.cosine_sim * 100).toFixed(1) }}%
               </span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- No Results Message -->
      <div v-if="results && results.length === 0 && !isLoading" class="text-center py-10 test-card-text">
        <p class="">No results found for your query.</p>
      </div>

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

<script setup>
import { ref } from 'vue';

const query = ref('');
const results = ref(null);
const isLoading = ref(false);
const error = ref(null);

const searchJobs = async () => {
  if (!query.value.trim()) {
    results.value = null;
    return;
  }

  isLoading.value = true;
  results.value = null;
  error.value = null;

  try {
    const response = await fetch(`http://localhost:8000/search?q=${encodeURIComponent(query.value)}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    results.value = data.results; // Access the nested 'results' array

  } catch (e) {
    console.error("Search failed:", e);
    error.value = e.message || "Failed to fetch search results. Make sure the backend API is running.";
  } finally {
    isLoading.value = false;
  }
};
</script>

<style>
</style>
