<script lang="ts" setup>
</script>

<template>
    <!-- Include this script tag or install `@tailwindplus/elements` via npm: -->
    <!-- <script src="https://cdn.jsdelivr.net/npm/@tailwindplus/elements@1" type="module"></script> -->
    <nav class="container mx-auto p-2 bg-gray-900">
        <div class="max-w-7xl px-2 ">
            <div class="relative flex h-16 items-center justify-between">
            <div class="flex flex-1 items-center justify-center sm:items-stretch sm:justify-start">
                <div class="flex shrink-0 items-center">
                <img src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=500" alt="Your Company" class="h-8 w-auto" />
                </div>
                <div class="hidden sm:ml-6 sm:block">
                <div class="flex space-x-4">
                    <NuxtLink class="rounded-md bg-gray-950/50 px-3 py-2 text-sm font-medium text-white hover:bg-white/5 hover:text-white" to="/">Index page</NuxtLink>
                    <NuxtLink class="rounded-md bg-gray-950/50 px-3 py-2 text-sm font-medium text-white hover:bg-white/5 hover:text-white" to="/statistics">Statistics page</NuxtLink>
                </div>
                </div>
            </div>
            <div class="absolute inset-y-0 right-0 flex items-center pr-2 sm:static sm:inset-auto sm:ml-6 sm:pr-0">
                <button type="button" class="relative rounded-full p-1 text-gray-400 hover:text-white focus:outline-2 focus:outline-offset-2 focus:outline-indigo-500">
                <span class="absolute -inset-1.5"></span>
                <span class="sr-only">View notifications</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" data-slot="icon" aria-hidden="true" class="size-6">
                    <path d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                </button>

            </div>
            </div>
        </div>
    </nav>
    
</template>

<style scoped>

</style>