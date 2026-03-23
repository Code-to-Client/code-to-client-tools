<template>
  <div>
    <div class="mb-8 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="dashboard-title mb-1 text-2xl font-bold text-gray-800 dark:text-gray-100">
          Contacts
          <span class="dashboard-title-underline block mt-1 h-0.5 w-12 rounded-full" />
        </h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Manage and filter your outreach contacts.</p>
      </div>
      <GlobalFilters />
    </div>

    <div class="card overflow-visible">
      <div class="card-body border-b border-gray-200 dark:border-gray-700">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <span class="text-sm text-gray-500 dark:text-gray-400 shrink-0">{{ contactCountLabel }}</span>
          <div class="flex flex-wrap items-center gap-2 ml-auto">
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300 shrink-0">Status: </span>
            <el-select v-model="statusFilter" placeholder="All" clearable class="!w-44">
              <el-option label="All" value="__all__" />
              <el-option v-for="(label, key) in STATUS_LABELS" :key="key" :label="label" :value="key" />
            </el-select>
            <NuxtLink to="/contacts/new">
              <el-button type="primary" :icon="Plus">Add contact</el-button>
            </NuxtLink>
          </div>
        </div>
      </div>

      <template v-if="contacts.loading">
        <div class="card-body">
          <p class="text-gray-500">Loading...</p>
        </div>
      </template>

      <template v-else-if="contacts.items.length === 0">
        <div class="card-body">
          <p class="text-gray-600 dark:text-gray-400">
            {{ hasActiveFilters ? 'No contacts match these filters. Try changing the status or vertical.' : "No contacts yet. Click 'Add contact' to create your first one." }}
          </p>
        </div>
      </template>

      <template v-else>
        <el-table
          :data="contacts.items"
          stripe
          class="contacts-table"
          max-height="calc(100vh - 280px)"
        >
        <el-table-column prop="company_name" label="Company" sortable>
          <template #default="{ row }">
            {{ row.company_name || '---' }}
          </template>
        </el-table-column>
        <el-table-column prop="vertical" label="Vertical" width="120" sortable />
        <el-table-column prop="contact_url" label="Contact page URL" min-width="200" sortable>
          <template #default="{ row }">
            <a
              v-if="row.contact_url"
              :href="row.contact_url"
              target="_blank"
              rel="noopener noreferrer"
              class="link-secondary-muted hover:underline truncate block max-w-xs"
              :title="row.contact_url"
            >
              {{ row.contact_url }}
            </a>
            <span v-else class="text-gray-400">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="140" sortable>
          <template #default="{ row }">
            <StatusBadge :status="row.status" />
          </template>
        </el-table-column>
        <el-table-column prop="contacted_at" label="Contacted" width="120" sortable>
          <template #default="{ row }">
            {{ formatContactedDate(row.contacted_at) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="120" align="center">
          <template #default="{ row }">
            <div class="flex items-center justify-center gap-1">
              <!-- <el-tooltip content="View" placement="top"> -->
                <el-button size="small" circle @click="openViewDialog(row)">
                  <el-icon><View /></el-icon>
                </el-button>
              <!-- </el-tooltip> -->
              <!-- <el-tooltip content="Edit" placement="top"> -->
                <NuxtLink :to="`/contacts/${row.id}`">
                  <el-button size="small" circle>
                    <el-icon><Edit /></el-icon>
                  </el-button>
                </NuxtLink>
              <!-- </el-tooltip> -->
            </div>
          </template>
        </el-table-column>
      </el-table>
      </template>
    </div>

    <el-dialog
      v-model="viewDialogVisible"
      width="1000px"
      @close="viewContact = null"
    >
      <template #header>
        <div class="flex items-center gap-3">
          <span>View contact</span>
          <span
            v-if="viewContact?.contact_source === 'MANUAL'"
            class="rounded px-2 py-0.5 texts-sm font-medium bg-gray-200 text-gray-700 dark:bg-gray-600 dark:text-gray-300"
          >
            Added manually
          </span>
        </div>
      </template>
      <div v-if="viewDialogLoading" class="py-8 text-center text-gray-500">Loading...</div>
      <div v-else-if="viewContact" class="view-dialog-body">
        <div class="card card-body min-w-0 space-y-5">
          <div class="flex items-baseline gap-2">
            <span class="texts-sm font-medium text-gray-500 dark:text-gray-400 shrink-0">Vertical: </span>
            <span class="text-gray-800 dark:text-gray-200">{{ viewContact.vertical || '—' }}</span>
          </div>

          <div class="flex items-baseline gap-2">
            <span class="texts-sm font-medium text-gray-500 dark:text-gray-400 shrink-0">Contact page URL: </span>
            <a
              v-if="viewContact.contact_url"
              :href="viewContact.contact_url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-gray-800 dark:text-gray-200 break-all min-w-0 link-secondary-muted hover:underline"
            >{{ viewContact.contact_url }}</a>
            <span v-else class="text-gray-800 dark:text-gray-200">—</span>
          </div>

          <div class="flex items-baseline gap-2">
            <span class="texts-sm font-medium text-gray-500 dark:text-gray-400 shrink-0">Status: </span>
            <StatusBadge :status="viewContact.status" />
          </div>

          <div class="flex items-baseline gap-2">
            <span class="text-sm font-medium text-gray-500 dark:text-gray-400 shrink-0">Contact name: </span>
            <span class="text-gray-800 dark:text-gray-200 min-w-0 break-words">{{ viewContact.contact_name || '—' }}</span>
          </div>
          <div class="flex items-baseline gap-2">
            <span class="texts-sm font-medium text-gray-500 dark:text-gray-400 shrink-0">Company name: </span>
            <span class="text-gray-800 dark:text-gray-200 min-w-0 break-words">{{ viewContact.company_name || '—' }}</span>
          </div>
          <div class="flex items-baseline gap-4">
            <div class="flex items-baseline gap-2">
              <span class="texts-sm font-medium text-gray-500 dark:text-gray-400 shrink-0">Email: </span>
              <span class="text-gray-800 dark:text-gray-200 min-w-0 break-words">{{ viewContact.email || '—' }}</span>
            </div>
            <div class="flex items-baseline gap-2">
              <span class="texts-sm font-medium text-gray-500 dark:text-gray-400 shrink-0">Phone: </span>
              <span class="text-gray-800 dark:text-gray-200 min-w-0 break-words">{{ viewContact.phone || '—' }}</span>
            </div>
          </div>
          <div class="flex items-baseline gap-4">
            <div class="flex items-baseline gap-2">
              <span class="texts-sm font-medium text-gray-500 dark:text-gray-400 shrink-0">City: </span>
              <span class="text-gray-800 dark:text-gray-200 min-w-0 break-words">{{ viewContact.city || '—' }}</span>
            </div>
            <div class="flex items-baseline gap-2">
              <span class="texts-sm font-medium text-gray-500 dark:text-gray-400 shrink-0">State: </span>
              <span class="text-gray-800 dark:text-gray-200 min-w-0 break-words">{{ viewContact.state || '—' }}</span>
            </div>
            <div class="flex items-baseline gap-2">
              <span class="texts-sm font-medium text-gray-500 dark:text-gray-400 shrink-0">Zip: </span>
              <span class="text-gray-800 dark:text-gray-200 min-w-0 break-words">{{ viewContact.postal_code || '—' }}</span>
            </div>
          </div>
          <div class="flex items-baseline gap-2">
            <span class="texts-sm font-medium text-gray-500 dark:text-gray-400 shrink-0">Main website URL: </span>
            <a
              v-if="viewContact.url"
              :href="viewContact.url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-gray-800 dark:text-gray-200 break-all min-w-0 link-secondary-muted hover:underline"
            >{{ viewContact.url }}</a>
            <span v-else class="text-gray-800 dark:text-gray-200">—</span>
          </div>
          
          <div class="flex items-baseline gap-2">
            <span class="texts-sm font-medium text-gray-500 dark:text-gray-400 shrink-0">Contacted date: </span>
            <span class="text-gray-800 dark:text-gray-200">{{ formatContactedDate(viewContact.contacted_at) }}</span>
          </div>
          
          <div v-if="viewContact.contact_source === 'MANUAL'" class="flex items-baseline gap-2">
            <span class="texts-sm font-medium text-gray-500 dark:text-gray-400 shrink-0">Source: </span>
            <span class="text-gray-800 dark:text-gray-200">Added manually</span>
          </div>
          <div class="flex items-baseline gap-2">
            <span class="texts-sm font-medium text-gray-500 dark:text-gray-400 shrink-0">Next action: </span>
            <span class="text-gray-800 dark:text-gray-200">{{ viewContact.next_action || '—' }}</span>
          </div>
          <div class="flex flex-col gap-2">
            <span class="texts-sm font-medium text-gray-500 dark:text-gray-400 shrink-0">Notes</span>
            <div
              class="notes-border min-w-0 rounded-lg border-1 px-3 py-2 text-gray-800 dark:text-gray-200 whitespace-pre-wrap max-h-40 overflow-y-auto"
            >
              {{ viewContact.notes || '—' }}
            </div>
          </div>
        </div>
        <div class="card card-body min-w-0">
          <StatusHistory :history="viewContact.status_history" />
        </div>
      </div>
      <!-- <el-divider class="p-0"/> -->
      <template #footer>
        <el-button @click="viewDialogVisible = false">Close</el-button>
        <NuxtLink
          v-if="viewContact"
          :to="`/contacts/${viewContact.id}`"
          @click="viewDialogVisible = false"
        >
          <el-button :icon="Edit" class="ml-3">Edit</el-button>
        </NuxtLink>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { STATUS_LABELS } from '~/stores/contacts'
import { Plus, Edit, View } from '@element-plus/icons-vue'

const contacts = useContactsStore()
const filters = useFiltersStore()
const statusFilter = ref('__all__')
const viewDialogVisible = ref(false)
const viewContact = ref(null)
const viewDialogLoading = ref(false)

async function openViewDialog(row) {
  viewDialogVisible.value = true
  viewContact.value = null
  viewDialogLoading.value = true
  try {
    viewContact.value = await contacts.fetchOne(row.id)
  } catch (_) {
    viewContact.value = row
  } finally {
    viewDialogLoading.value = false
  }
}

function statusForApi() {
  const v = statusFilter.value
  return (v === '__all__' || v === '' || v == null) ? undefined : v
}

const hasActiveFilters = computed(() =>
  statusForApi() != null ||
  (filters.vertical || null) != null ||
  (filters.zip || null) != null ||
  (filters.cityState || null) != null
)

const contactCountLabel = computed(() => {
  if (contacts.loading) return '—'
  const n = contacts.items.length
  return n === 1 ? '1 contact' : `${n} contacts`
})

function formatContactedDate(value) {
  if (!value) return '—'
  const s = typeof value === 'string' ? value : value.toISOString?.() ?? String(value)
  return s.slice(0, 10)
}

function fetchWithFilters() {
  contacts.fetchList({
    status: statusForApi(),
    vertical: filters.vertical || undefined,
    postal_code: filters.zip || undefined,
    city_state: filters.cityState || undefined,
  })
}

watch(statusFilter, (v) => {
  if (v === '' || v == null) { statusFilter.value = '__all__'; nextTick(fetchWithFilters); return }
  fetchWithFilters()
})

watch(() => [filters.vertical, filters.zip, filters.cityState], fetchWithFilters)

onMounted(() => {
  fetchWithFilters()
})
</script>

<style scoped>
.view-dialog-body {
  display: grid;
  grid-template-columns: 1fr 22rem;
  gap: 1.5rem;
  align-items: start;
  width: 100%;
}
.notes-border {
  border: 1px solid rgb(107 114 128 / 0.4);
}
</style>
