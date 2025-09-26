<!-- components/LocationTreemap.vue -->
<template>
  <div class="treemap-container">
    <client-only>
      <VChart 
        :option="chartOption" 
        :style="{ height: '500px' }"
        autoresize
      />
    </client-only>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { TreemapChart } from 'echarts/charts'
import { TooltipComponent, TitleComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useChartTheme } from '~/composables/useChartTheme'

// Register ECharts components
use([CanvasRenderer, TreemapChart, TooltipComponent, TitleComponent])
const { chartTheme } = useChartTheme()

interface LocationData {
  location: string
  count: number
}

const props = defineProps<{
  data: LocationData[]
  title?: string
}>()

// Transform data here in the component
const chartOption = computed(() => {
  // Transform location/count to name/value for ECharts
  const treemapData = props.data.map(item => ({
    name: item.location,
    value: item.count
  }))

  return {
    ...chartTheme.value, // Spread theme first

    title: {
      ...chartTheme.value.title,
      text: props.title || 'Job Locations Distribution',
      left: 'center',
      textStyle: {
        fontSize: 20
      }
    },
    tooltip: {
        ...chartTheme.value.tooltip,
      formatter: (params: any) => {
        return `${params.name}<br/>Jobs: ${params.value}`
      }
    },
    series: [{
      type: 'treemap',
      data: treemapData,
      leafDepth: 1,
      roam: false,
      nodeClick: 'zoomToNode',
      breadcrumb: {
        show: false
      },
      label: {
        show: true,
        formatter: (params: any) => {
          const total = props.data.reduce((sum, item) => sum + item.count, 0)
          const percentage = (params.value / total * 100).toFixed(1)
          if (params.value > 5) {
            return `${params.name}\n${params.value} jobs\n(${percentage}%)`
          }
          return params.name
        },
        fontSize: 12
      },
      itemStyle: {
        borderColor: '#fff',
        borderWidth: 2,
        gapWidth: 1
      },
      color: [
        '#5470c6', '#91cc75', '#fac858', '#ee6666',
        '#73c0de', '#3ba272', '#fc8452', '#9a60b4'
      ]
    }]
  }
})
</script>

<style scoped>
.treemap-container {
  width: 100%;
  min-height: 500px;
}
</style>