<!-- pages/statistics.vue -->
<template>
  <div class="statistics-page">
    <div class="content-wrapper">
      <h1>Job Market Statistics</h1>
      
      <div v-if="error" class="error">
        {{ error }}
      </div>
      
      <div v-else class="charts-grid">
        <!-- Treemap for locations -->
        <div class="chart-section full-width">
          <LocationTreemap 
            v-if="jobsPerLocation.length > 0" 
            :data="jobsPerLocation" 
            title="Jobs by Location"
          />
        </div>

        <!-- Bar chart for top companies -->
        <div class="chart-section">
          <BarChart 
            v-if="topCompanies.length > 0"
            :data="topCompanies"
            title="Top Hiring Companies"
            :horizontal="false"
          />
        </div>

        <!-- Pie chart for location distribution -->
        <div class="chart-section">
          <PieChart
            v-if="jobsPerLocation.length > 0"
            :data="jobsPerLocation"
            title="Location Distribution"
            :max-items="8"
            :donut="true"
          />
        </div>

        <!-- Stacked bar chart for company job types -->
        <div class="chart-section full-width">
          <BarChart
            v-if="companyOfferType.length > 0"
            :data="companyOfferType"
            title="Engineering vs Other Roles by Company"
            type="stacked"
            height="500px"
          />
        </div>

        <!-- Alternative: Horizontal bar chart -->
        <div class="chart-section">
          <BarChart
            v-if="topCompanies.length > 0"
            :data="topCompanies.slice(0, 10)"
            title="Top 10 Companies"
            :horizontal="true"
            height="400px"
          />
        </div>

        <!-- Pie chart for top companies -->
        <div class="chart-section">
          <PieChart
            v-if="topCompanies.length > 0"
            :data="topCompanies"
            title="Company Distribution"
            :max-items="12"
            :show-legend="true"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'

const stats = useStatsStore()
await stats.fetchStatistics()

const { 
  jobsPerLocation, 
  topCompanies, 
  companyOfferType, 
  error 
} = storeToRefs(stats)
</script>

<style scoped>
.statistics-page {
  min-height: 100vh;
  background: #f5f5f5;  /* Optional: light background to see the content area */
}

.content-wrapper {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 0;
  width: 100%;
}

.content-wrapper > * {
  grid-column: 2 / 12;  /* Content spans from column 2 to 11 (10 columns) */
}

h1 {
  text-align: center;
  margin: 2rem 0;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-section {
  min-height: 400px;
}

.full-width {
  grid-column: 1 / -1;
}

.error {
  color: red;
  text-align: center;
  padding: 2rem;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .content-wrapper > * {
    grid-column: 2 / 12;  /* Still use 10 columns on medium screens */
  }
  
  .charts-grid {
    grid-template-columns: 1fr;  /* Stack charts vertically */
  }
}

@media (max-width: 768px) {
  .content-wrapper > * {
    grid-column: 1 / 13;  /* Use full width on mobile */
    padding: 0 1rem;  /* Add padding instead */
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>