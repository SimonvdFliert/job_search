export const useChartTheme = () => {
  const colorMode = useColorMode()
  
  const theme = computed(() => {
    const isDark = colorMode.value === 'dark'
    
    return {
      // Text colors from your CSS variables
      textColor: isDark ? '#000000' : '#000000',
      mutedTextColor: isDark ? '#000000' : '#000000',
      
      // Lines and borders
      axisLineColor: isDark ? '#000000' : '#000000',
      splitLineColor: isDark ? '#000000' : '#000000',
      
      // Tooltip
      tooltipBg: isDark ? '#000000' : '#000000',
      tooltipBorder: isDark ? '#000000' : '#000000',
    }
  })
  
  // Return ready-to-spread theme options
  const chartTheme = computed(() => ({
    backgroundColor: 'transparent', // Inherit from parent
    
    textStyle: {
      color: theme.value.textColor
    },
    
    title: {
      textStyle: {
        color: theme.value.textColor
      }
    },
    
    legend: {
      textStyle: {
        color: theme.value.mutedTextColor
      }
    },
    
    tooltip: {
      backgroundColor: theme.value.tooltipBg,
      borderColor: theme.value.tooltipBorder,
      borderWidth: 1,
      textStyle: {
        color: theme.value.textColor
      }
    },
    
    xAxis: {
      axisLine: {
        lineStyle: { color: theme.value.axisLineColor }
      },
      axisLabel: {
        color: theme.value.mutedTextColor
      },
      splitLine: {
        lineStyle: { color: theme.value.splitLineColor }
      }
    },
    
    yAxis: {
      axisLine: {
        lineStyle: { color: theme.value.axisLineColor }
      },
      axisLabel: {
        color: theme.value.mutedTextColor
      },
      splitLine: {
        lineStyle: { color: theme.value.splitLineColor }
      }
    }
  }))
  
  return { chartTheme, theme }
}