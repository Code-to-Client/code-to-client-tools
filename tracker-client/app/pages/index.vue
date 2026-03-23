<template>
  <div>
    <div class="mb-8 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="dashboard-title mb-1 text-2xl font-bold text-gray-800 dark:text-gray-100">
          Outreach Dashboard
          <span class="dashboard-title-underline block mt-1 h-0.5 w-12 rounded-full" />
        </h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Overview of your contact form outreach and pipeline.</p>
      </div>
      <GlobalFilters />
    </div>

    <template v-if="dashboard.loading">
      <div class="card card-body">
        <p class="text-gray-500">Loading...</p>
      </div>
    </template>

    <template v-else-if="dashboard.data">
      <div class="mb-1 flex items-center justify-between">
        <h2 class="section-title section-title--secondary text-lg font-semibold text-gray-800 dark:text-gray-100">Key metrics</h2>
        <el-radio-group v-model="statusMode" Xsize="small">
          <el-radio-button label="pct_contacted">% Contacted</el-radio-button>
          <el-radio-button label="pct_visitors">% Visitors</el-radio-button>
        </el-radio-group>
      </div>
      <div class="mb-8 grid grid-cols-3 gap-4">
        <MetricCard label="Contacts Sent" :value="dashboard.data.contacts_sent" :percentage="statusMode === 'pct_contacted' ? '100%' : null" />
        <MetricCard label="Website Visitors" :value="dashboard.data.visitor_count" :percentage="statusMode === 'pct_visitors' ? '100%' : null" />
        <MetricCard label="Total Responses" :value="dashboard.data.total_responses" :percentage="pctValue(dashboard.data.total_responses)" />
        <MetricCard label="Design Partner Prospects" :value="dashboard.data.design_partner_prospects" :percentage="pctValue(dashboard.data.design_partner_prospects)" />
        <MetricCard label="Waitlist Signups" :value="dashboard.data.waitlist_signups" :percentage="pctValue(dashboard.data.waitlist_signups)" />
        <MetricCard label="Other Prospects" :value="dashboard.data.other_prospects" :percentage="pctValue(dashboard.data.other_prospects)" />
      </div>

      <h2 class="section-title mb-4 text-lg font-semibold text-gray-800 dark:text-gray-100">Contacts by status</h2>
      <div class="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
        <StatusCard label="Contacted" :value="dashboard.data.by_status.CONTACTED" variant="CONTACTED" />
        <StatusCard label="Design Partner Prospect" :value="dashboard.data.by_status.DESIGN_PARTNER_PROSPECT" variant="DESIGN_PARTNER_PROSPECT" />
        <StatusCard label="Waitlisted" :value="dashboard.data.by_status.WAITLISTED" variant="WAITLISTED" />
        <StatusCard label="Other Prospect" :value="dashboard.data.by_status.OTHER_PROSPECT" variant="OTHER_PROSPECT" />
        <StatusCard label="Discovery Call" :value="dashboard.data.by_status.DISCOVERY_CALL" variant="DISCOVERY_CALL" />
        <StatusCard label="Design Partner" :value="dashboard.data.by_status.DESIGN_PARTNER" variant="DESIGN_PARTNER" />
        <StatusCard label="Customer" :value="dashboard.data.by_status.CUSTOMER" variant="CUSTOMER" />
        <StatusCard label="Not Interested" :value="dashboard.data.by_status.NOT_INTERESTED" variant="NOT_INTERESTED" />
      </div>

      <!-- <div class="flex gap-3">
        <NuxtLink to="/contacts">
          <el-button type="primary">View contacts</el-button>
        </NuxtLink>
        <NuxtLink to="/contacts/new">
          <el-button :icon="Plus">Add contact</el-button>
        </NuxtLink>
      </div> -->
    </template>

    <template v-else>
      <p class="mb-8 text-gray-600 dark:text-gray-400">
        You haven't logged any outreach yet. After your next contact-form session, run the autofill script;
        new contacts will appear here. When someone replies, update their status and add details (company, notes, etc.).
      </p>
      <h2 class="section-title section-title--secondary mb-4 text-lg font-semibold text-gray-800 dark:text-gray-100">Key metrics</h2>
      <div class="mb-8 grid grid-cols-3 gap-4">
        <MetricCard label="Contacts Sent" :value="0" />
        <MetricCard label="Website Visitors" :value="0" />
        <MetricCard label="Total Responses" :value="0" />
        <MetricCard label="Design Partner Prospects" :value="0" />
        <MetricCard label="Waitlist Signups" :value="0" />
        <MetricCard label="Other Prospects" :value="0" />
      </div>
      <div class="flex gap-3">
        <NuxtLink to="/contacts">
          <el-button type="primary">View contacts</el-button>
        </NuxtLink>
        <NuxtLink to="/contacts/new">
          <el-button :icon="Plus">Add contact</el-button>
        </NuxtLink>
      </div>
    </template>
  </div>
</template>

<script setup>
import { Plus } from '@element-plus/icons-vue'

const statusMode = ref('pct_contacted')

function pctValue(count) {
  const n = count ?? 0
  if (statusMode.value === 'pct_contacted') {
    const total = dashboard.data?.contacts_sent
    return total ? `${Math.round(n / total * 100)}%` : null
  }
  if (statusMode.value === 'pct_visitors') {
    const total = dashboard.data?.visitor_count
    return total ? `${Math.round(n / total * 100)}%` : null
  }
  return null
}

const dashboard = useDashboardStore()
const filters = useFiltersStore()

function fetchDashboard() {
  dashboard.fetch({
    vertical: filters.vertical || undefined,
    postal_code: filters.zip || undefined,
    city_state: filters.cityState || undefined,
  })
}

watch(() => [filters.vertical, filters.zip, filters.cityState], fetchDashboard)

onMounted(() => {
  fetchDashboard()
})

</script>
