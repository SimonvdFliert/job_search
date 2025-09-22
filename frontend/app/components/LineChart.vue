<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{ data: { name: string; value: number }[] }>()
// Chart styling
const chartStyle = { height: '400px', width: '100%' }

// Process and sort the data
const processedData = computed(() => {
  // Sort data by date
  const sortedData = [...props.data].sort((a, b) =>
    // console.log('a.date, b.date', a.date, b.date) ||
    new Date(a.date) - new Date(b.date)
  )
  
  // Extract dates and counts into separate arrays
  const postDates = sortedData.map(item => item.date)
  const counts = sortedData.map(item => item.count)
  return { postDates, counts }
})

// Alternative: Line chart for better time series visualization
const lineChartOptions = computed(() => ({
  tooltip: {
    trigger: 'axis',
    formatter: (params) => {
      const date = params[0].axisValue
      const count = params[0].value
      return `Date: ${date}<br/>Posts: ${count}`
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '15%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: processedData.value.postDates,
    boundaryGap: false,
    axisLabel: {
      rotate: 45,
      interval: 'auto'
    }
  },
  yAxis: {
    type: 'value',
    name: 'Post Count'
  },
  series: [
    {
      name: 'Posts',
      type: 'line',
      data: processedData.value.counts,
      smooth: true,
      areaStyle: {
        opacity: 0.3
      },
      itemStyle: {
        color: '#91cc75'
      }
    }
  ]
}))
</script>

<template>
    <div class="chart-section">
        <h2>Line Chart</h2>
        <client-only>
          <VChart 
            :option="lineChartOptions" 
            :style="chartStyle"
            autoresize 
          />
        </client-only>
      </div>
</template>