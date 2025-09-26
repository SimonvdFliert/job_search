<template>
  <div class="min-h-screen md:grid md:grid-cols-12">
      <div class=" min-h-screen font-sans md:col-start-2 md:col-span-10">
        <div class="container mx-auto px-4">
          <h1 class="text-4xl font-bold mb-2 ">Statistics</h1>
          <p class=" mb-8">
            Placeholder.
          </p>
        </div>
        <!-- <Cards />
        <Cards />
        <Cards />
        <div> Small card of total active Job offerings (of the last 30 days)</div>
        <div> Small card of most recent Job offerings</div>
        <div> Small card of total companies with active Job offerings</div> -->




        <div v-if="error" class="text-red-600">{{ error }}</div>
        <LineChart v-else :data="jobsPerDay" />

        <!-- Bar chart for top companies -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <TreeMap :data="jobsPerLocation" />

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

          <div class="chart-section ">
            <BarChart 
              v-if="topCompanies.length > 0"
              :data="topCompanies"
              title="Top Hiring Companies"
              :horizontal="false"
            />
          </div>


          <div class="chart-section full-width">
            <BarChart
              v-if="companyOfferType.length > 0"
              :data="companyOfferType"
              title="Engineering vs Other Roles by Company"
              type="stacked"
              height="500px"
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
const { jobsPerDay, jobsPerLocation, topCompanies, companyOfferType, error } = storeToRefs(stats)
console.log('jobsPerLocation in statistics.vue:', jobsPerLocation.value);

const colorMode = useColorMode()

console.log(colorMode.preference)

</script>

<style scoped>
body {
  background-color: #fff;
  color: rgba(0,0,0,0.8);
}
.dark-mode body {
  background-color: #091a28;
  color: #ebf4f1;
}
.sepia-mode body {
  background-color: #f1e7d0;
  color: #433422;
}
</style>
