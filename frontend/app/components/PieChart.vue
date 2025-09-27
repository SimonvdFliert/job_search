<!-- components/PieChart.vue -->
<template>
  <div class="bg-card border">
    <client-only>
      <VChart 
        :option="chartOption" 
        :style="{ height: height }"
        autoresize
      />
    </client-only>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, TitleComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useChartTheme } from '~/composables/useChartTheme'

// Register ECharts components
use([CanvasRenderer, PieChart, TooltipComponent, TitleComponent, LegendComponent])
const { chartTheme } = useChartTheme()

interface PieData {
  name?: string
  location?: string
  company?: string
  count?: number
  value?: number
  total?: number
}

const props = withDefaults(defineProps<{
  data: PieData[]
  title?: string
  height?: string
  showLegend?: boolean
  maxItems?: number  // Limit items shown (group rest as "Others")
  donut?: boolean    // Show as donut chart
}>(), {
  height: '400px',
  showLegend: true,
  maxItems: 10,
  donut: false
})

const chartOption = computed(() => {
  // Prepare data

  let chartData = props.data.map(item => ({
    name: item.name || item.location || item.company || '',
    value: item.count || item.value || item.total || 0
  }))

  // If too many items, group the smaller ones as "Others"
  if (props.maxItems && chartData.length > props.maxItems) {
    const topItems = chartData.slice(0, props.maxItems - 1)
    const otherItems = chartData.slice(props.maxItems - 1)
    const othersValue = otherItems.reduce((sum, item) => sum + item.value, 0)
    
    chartData = [
      ...topItems,
      { name: 'Others', value: othersValue }
    ]
  }

  const total = chartData.reduce((sum, item) => sum + item.value, 0)

  return {
    // ...chartTheme.value, // Spread theme first
    backgroundColor: 'transparent', // IMPORTANT for pie charts!
    title: {
      // ...chartTheme.value.title,
      text: props.title || 'Distribution',
      left: 'center',
      textStyle: {
        color: chartTheme.value.textStyle.color,
        fontSize: 16,
        fontWeight: 500
      }
    },
    tooltip: {
      ...chartTheme.value.tooltip,
      trigger: 'item',
      formatter: (params: any) => {
        const percentage = ((params.value / total) * 100).toFixed(1)
        return `${params.name}<br/>Count: ${params.value} (${percentage}%)`
      }
    },
    legend: props.showLegend ? {
      ...chartTheme.value.legend,
      type: 'scroll',
      orient: 'vertical',
      right: 10,
      top: 'center',
      formatter: (name: string) => {
        const item = chartData.find(d => d.name === name)
        if (item) {
          const percentage = ((item.value / total) * 100).toFixed(1)
          return `${name} (${item.value} - ${percentage}%)`
        }
        return name
      }
    } : undefined,
    series: [{
      type: 'pie',
      radius: props.donut ? ['40%', '70%'] : '70%',
      center: props.showLegend ? ['40%', '50%'] : ['50%', '50%'],
      data: chartData,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      },
      label: {
        show: chartData.length <= 8,  // Hide labels if too many items
        lineStyle: {
          color: chartTheme.value.textStyle.color // Theme the label lines
        },
        formatter: (params: any) => {
          if (params.value < total * 0.03) return ''  // Hide tiny slices
          return `${params.name}\n${params.value}`
        }
      },
      labelLine: {
        show: chartData.length <= 8
      },
      itemStyle: {
        borderRadius: props.donut ? 10 : 0,
        borderColor: '#fff',
        borderWidth: 2
      }
    }],
    color: [
      '#5470c6', '#91cc75', '#fac858', '#ee6666',
      '#73c0de', '#3ba272', '#fc8452', '#9a60b4',
      '#ea7ccc', '#ff9f7f', '#ffdb5c', '#8378ea'
    ]
  }
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>