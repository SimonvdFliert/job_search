// stores/stats.ts
import { defineStore, storeToRefs } from 'pinia'

type DayPoint = { date: string; count: number }
type NamedValue = { name: string; value: number }
type OfferTypeRow = { company: string; engineer: number; other: number; total: number }

type ApiStats = {
  jobs_per_day: DayPoint[]
  jobs_per_location: NamedValue[]
  top_companies: NamedValue[]
  company_offer_type: OfferTypeRow[]
}

export const useStatsStore = defineStore('statistics', {
  state: () => ({
    jobsPerDay: [] as DayPoint[],
    jobsPerLocation: [] as NamedValue[],
    topCompanies: [] as NamedValue[],
    companyOfferType: [] as OfferTypeRow[],
    loaded: false,
    error: null as string | null,
  }),
  actions: {
    async fetchStatistics(force = false) {
      if (this.loaded && !force) return
      this.error = null
      try {
        const { public: { apiBase } } = useRuntimeConfig()
        const infos = await $fetch<ApiStats>(`${apiBase}/statistics/CTE`)
        console.log('Fetched statistics:', infos)
        this.jobsPerDay = infos.jobs_per_day
        this.jobsPerLocation = infos.jobs_per_location
        this.topCompanies = infos.top_companies
        this.companyOfferType = infos.company_offer_type
        this.loaded = true
      } catch (e: any) {
        this.error = e?.message ?? 'Failed to load statistics'
      }
    }
  }
})
