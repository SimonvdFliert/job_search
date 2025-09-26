<!-- components/BarChart.vue -->
<template>
  <div class="chart-container dark:bg-gray-800">
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
import { BarChart } from 'echarts/charts'
import { TooltipComponent, TitleComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// Register ECharts components
use([CanvasRenderer, BarChart, TooltipComponent, TitleComponent, GridComponent, LegendComponent])
//
//const colorMode = useColorMode() // from @nuxtjs/color-mode
//const theme = computed(() => (colorMode.value === 'dark' ? 'dark' : 'light'))

interface BarData {
  name?: string
  company?: string
  count?: number
  value?: number
  engineer?: number
  other?: number
  total?: number
}

const props = withDefaults(defineProps<{
  data: BarData[]
  title?: string
  height?: string
  type?: 'simple' | 'stacked'  // For company_offer_type data
  horizontal?: boolean
}>(), {
  height: '400px',
  type: 'simple',
  horizontal: false
})

const chartOption = computed(() => {
  // Handle different data formats
  if (props.type === 'stacked' && props.data[0]?.engineer !== undefined) {
    // Stacked bar chart for company_offer_type data
    const companies = props.data.map(item => item.company || item.name || '')
    const engineerData = props.data.map(item => item.engineer || 0)
    const otherData = props.data.map(item => item.other || 0)

    return {
      //backgroundColor: '#1e293b', // chart background
      title: {
        text: props.title || 'Company Job Types',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params: any) => {
          const company = params[0].axisValue
          const engineer = params[0].value
          const other = params[1].value
          const total = engineer + other
          return `${company}<br/>
                  Engineers: ${engineer}<br/>
                  Other: ${other}<br/>
                  Total: ${total}`
        }
      },
      legend: {
        data: ['Engineering', 'Other Roles'],
        bottom: 0
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '10%',
        top: '15%',
        containLabel: true
      },
      xAxis: {
        type: props.horizontal ? 'value' : 'category',
        data: props.horizontal ? undefined : companies,
        axisLabel: {
          interval: 0,
          rotate: 45,
          fontSize: 10
        }
      },
      yAxis: {
        type: props.horizontal ? 'category' : 'value',
        data: props.horizontal ? companies : undefined
      },
      series: [
        {
          name: 'Engineering',
          type: 'bar',
          stack: 'total',
          data: engineerData,
          itemStyle: { color: '#5470c6' }
        },
        {
          name: 'Other Roles',
          type: 'bar',
          stack: 'total',
          data: otherData,
          itemStyle: { color: '#91cc75' }
        }
      ]
    }
  } else {
    // Simple bar chart
    const labels = props.data.map(item => item.name || item.company || '')
    const values = props.data.map(item => item.count || item.value || item.total || 0)

    return {
    //backgroundColor: '#1e293b', // chart background
    //textStyle: { color: '#f1f5f9' },
 
      title: {
        text: props.title || 'Top Companies',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params: any) => {
          return `${params[0].name}<br/>Jobs: ${params[0].value}`
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '15%',
        containLabel: true
      },
      xAxis: {
            axisLine: { lineStyle: { color: '#94a3b8' } },
 
        type: props.horizontal ? 'value' : 'category',
        data: props.horizontal ? undefined : labels,
        axisLabel: {
          // color: '#e2e8f0',
          interval: 0,
          rotate: 45,
          fontSize: 10,
          overflow: 'truncate',
          width: 80
        }
      },
      yAxis: {
        // axisLine: { lineStyle: { color: '#94a3b8' } },
        // splitLine: { lineStyle: { color: '#334155' } },
        type: props.horizontal ? 'category' : 'value',
        data: props.horizontal ? labels : undefined,
        axisLabel: props.horizontal ? {
          overflow: 'truncate',
          width: 100
        } : {}
      },
      series: [{
        type: 'bar',
        data: values,
        itemStyle: {
          color: '#5470c6',
          borderRadius: [4, 4, 0, 0]
        },
        label: {
          show: props.data.length <= 10,  // Only show labels if not too crowded
          position: 'top',
          formatter: '{c}'
        }
      }]
    }
  }
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>