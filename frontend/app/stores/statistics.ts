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
  stats_summary: Record<string, number>
}

export const useStatsStore = defineStore('statistics', {
  state: () => ({
    jobsPerDay: [] as DayPoint[],
    jobsPerLocation: [] as NamedValue[],
    topCompanies: [] as NamedValue[],
    companyOfferType: [] as OfferTypeRow[],
    stats_summary: {} as Record<string, number>,
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
        this.jobsPerDay = infos.jobs_per_day
        this.jobsPerLocation = infos.jobs_per_location
        this.topCompanies = infos.top_companies
        this.companyOfferType = infos.company_offer_type
        this.stats_summary = infos.stats_summary
        this.loaded = true
      } catch (e: any) {
        this.error = e?.message ?? 'Failed to load statistics'
      }
    }
  }
})
