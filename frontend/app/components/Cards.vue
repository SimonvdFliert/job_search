<template>
    <div class="max-w-sm rounded overflow-hidden shadow-lg bg-card rounded">
        <div class="flex items-start justify-between m-2 pl-2">
            <div>
                    <p class="text-card-header text-sm font-medium">
                    {{ label }}
                    </p>
                    <p class="text-card-text text-2xl font-bold mt-1">
                    {{ formattedValue }}
                    </p>
                    <p v-if="subtext" class="text-card-text text-s mt-2">
                    {{ subtext }}
                    </p>
            </div>
            <div v-if="icon" class="text-accent">
                <component :is="icon" class="w-8 h-8" />
            </div>
        </div>

        <div v-if="trend" class="mt-3 flex items-center text-sm pl-2">
        <span 
            :class="trend > 0 ? 'text-green-600' : 'text-red-600'"
            class="flex items-center"
        >
            <svg v-if="trend > 0" class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" />
            </svg>
            <svg v-else class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M14.707 12.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l2.293-2.293a1 1 0 011.414 0z" />
            </svg>
            {{ Math.abs(trend) }}%
        </span>
        <span class="text-content-secondary ml-2 text-card-text">vs last period</span>
        </div>
    </div>
</template>

<script setup lang="ts">
// No script logic needed for this static card component
interface Props {
  label: string
  value: number | string
  subtext?: string
  icon?: any
  trend?: number
  format?: 'number' | 'date' | 'currency'
}

const props = withDefaults(defineProps<Props>(), {
  format: 'number'
})

const formattedValue = computed(() => {
  if (props.format === 'number') {
    return typeof props.value === 'number' 
      ? props.value.toLocaleString() 
      : props.value
  }
  if (props.format === 'currency') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(Number(props.value))
  }
  if (props.format === 'date' && props.value) {
    return new Date(props.value).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }
  return props.value
})
</script>

<style scoped>
</style>