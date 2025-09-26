import * as echarts from 'echarts/core'
import dark from 'echarts/theme/dark.json'

const myDarkTheme = {
  backgroundColor: '#1e293b',          // Tailwind slate-800
  textStyle: {
    color: '#f1f5f9',                  // Tailwind slate-100
  },
  color: [
    '#38bdf8', '#34d399', '#fbbf24',   // cyan-400, green-400, amber-400
    '#f87171', '#a78bfa', '#f472b6',   // red-400, violet-400, pink-400
  ],
  axisPointer: {
    lineStyle: { color: '#94a3b8' },   // slate-400
  },
  // you can also override grid, legend, tooltip, etc.
}

echarts.registerTheme('myDark', myDarkTheme)
