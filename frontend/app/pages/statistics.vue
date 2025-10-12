<template>
  <div class="min-h-screen md:grid md:grid-cols-12">
      <div class=" min-h-screen font-sans md:col-start-2 md:col-span-10">

        <div class="grid grid-cols-4 mb-5 mt-4 rounded"> 
          <Cards 
          label="Active Job Listings"
          :value="stats_summary?.total_active_jobs || 0"
          subtext="Last 30 days"/>
          <Cards 
            label="Number of Companies"
            :value="stats_summary?.total_active_companies || 0"
            subtext="Last 30 days"/>
          <Cards 
            label="Latest Job Posting"
            :value="stats_summary?.latest_job_date || 'Unknown'"
            subtext="Last 30 days"/>
        </div>

        <div v-if="error" class="text-red-600">{{ error }}</div>
        <LineChart v-else :data="jobsPerDay" />

        <!-- Bar chart for top companies -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <TreeMap :data="jobsPerLocation" />

          <!-- Pie chart for location distribution
          <div class="chart-section">
            <PieChart
              v-if="jobsPerLocation.length > 0"
              :data="jobsPerLocation"
              title="Location Distribution"
              :max-items="8"
              :donut="true"
            />
          </div> -->
          <div class="chart-section full-width">
            <BarChart
              v-if="companyOfferType.length > 0"
              :data="companyOfferType"
              title="Engineering vs Other Roles by Company"
              type="stacked"
              height="500px"
            />
          </div>
          <div class="chart-section full-width ">
            <BarChart 
              v-if="topCompanies.length > 0"
              :data="topCompanies"
              title="Top Hiring Companies"
              :horizontal="false"
            />
          </div>
        </div>
      </div>

  </div>

</template>

<script setup>
import { ref, computed } from 'vue'

const stats = useStatsStore()
await stats.fetchStatistics() // runs on server for SSR, hydrates to client
const { jobsPerDay, jobsPerLocation, topCompanies, stats_summary, companyOfferType, error } = storeToRefs(stats)

const colorMode = useColorMode()

</script>

<style scoped>
</style>
