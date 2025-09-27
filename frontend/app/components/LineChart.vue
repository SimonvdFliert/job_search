<script setup lang="ts">
import { ref, computed } from 'vue'
import { useChartTheme } from '~/composables/useChartTheme'

const props = defineProps<{ data: { name: string; value: number }[] }>()
// Chart styling
const chartStyle = { height: '400px', width: '100%' }
const { chartTheme } = useChartTheme()

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
  ...chartTheme.value, // Spread theme first

  title: {
        ...chartTheme.value.title,
        text: 'Job Posts Over Time',
        left: 'center'
      },

  tooltip: {
    ...chartTheme.value.tooltip,
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
    ...chartTheme.value.xAxis,
    type: 'category',
    data: processedData.value.postDates,
    boundaryGap: false,
    axisLabel: {
      ...chartTheme.value.xAxis.axisLabel,
      rotate: 45,
      interval: 'auto'
    }
  },
  yAxis: {
    ...chartTheme.value.yAxis,
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
        color: chartTheme.value.textStyle.color,
      }
    }
  ]
}))
</script>

<template>
    <div class="chart-section bg-card border mb-5">
        <client-only>
          <VChart 
            :option="lineChartOptions" 
            :style="chartStyle"
            autoresize 
          />
        </client-only>
      </div>
</template>