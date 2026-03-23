<template>
  <div>
    <div class="mb-8 flex flex-wrap items-center justify-between gap-4">
      <div>
        <h1 class="dashboard-title mb-1 text-2xl font-bold text-gray-800 dark:text-gray-100">
          Verticals
          <span class="dashboard-title-underline block mt-1 h-0.5 w-12 rounded-full" />
        </h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Configure verticals used when categorizing contacts. Add, edit, or remove verticals here.
        </p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">Add vertical</el-button>
    </div>

    <div class="card">
      <template v-if="verticals.loading">
        <div class="card-body">
          <p class="text-gray-500">Loading...</p>
        </div>
      </template>
      <template v-else-if="verticals.items.length === 0">
        <div class="card-body">
          <p class="text-gray-600 dark:text-gray-400">
            No verticals yet. Click "Add vertical" to create one (e.g. Legal, Property Management).
          </p>
        </div>
      </template>
      <template v-else>
        <el-table :data="verticals.items" stripe>
          <el-table-column prop="name" label="Name" min-width="200" />
          <el-table-column label="Website visitors" width="140" align="right">
            <template #default="{ row }">
              {{ row.website_visitors != null ? formatNumber(row.website_visitors) : '—' }}
            </template>
          </el-table-column>
          <el-table-column label="Contacts" width="100" align="right">
            <template #default="{ row }">
              {{ row.contact_count ?? 0 }}
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="160" align="right">
            <template #default="{ row }">
              <el-button size="small" @click="openEditDialog(row)">Edit</el-button>
              <el-tooltip
                v-if="(row.contact_count ?? 0) > 0"
                content="Used by at least one contact. Reassign their vertical first."
                placement="top"
              >
              <el-button
                size="small"
                type="danger"
                plain
                disabled
              >
                Delete
              </el-button>
              </el-tooltip>
              <el-button
                v-else
                size="small"
                type="danger"
                plain
                :loading="deletingId === row.id"
                @click="confirmDelete(row)"
              >
                Delete
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </template>
    </div>

    <!-- Create / Edit dialog -->
    <el-dialog
      v-model="formDialogVisible"
      :title="editingVertical ? 'Edit vertical' : 'Add vertical'"
      width="440px"
      @closed="resetFormDialog"
    >
      <el-form :model="form" label-width="120px">
        <el-form-item label="Name" required>
          <el-input v-model="form.name" placeholder="e.g. Legal, Property Management" maxlength="255" show-word-limit />
        </el-form-item>
        <el-form-item label="Website visitors">
          <el-input
            v-model="form.website_visitors"
            type="number"
            min="0"
            placeholder="From host (e.g. Netlify)"
            class="w-full"
          />
          <div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Visitor count from your website host (e.g. Netlify)
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="saving" @click="submitForm">
          {{ editingVertical ? 'Save' : 'Add' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Delete confirm -->
    <el-dialog v-model="deleteDialogVisible" title="Delete vertical" width="400px">
      <p v-if="verticalToDelete">
        Are you sure you want to delete <strong>{{ verticalToDelete.name }}</strong>?
        This vertical is not used by any contacts.
      </p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button type="danger" plain :loading="deletingId === verticalToDelete?.id" @click="doDelete">
          Delete
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { Plus } from '@element-plus/icons-vue'

const verticals = useVerticalsStore()
const formDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const editingVertical = ref(null)
const verticalToDelete = ref(null)
const saving = ref(false)
const deletingId = ref(null)

const form = reactive({
  name: '',
  website_visitors: '',
})

function formatNumber(n) {
  if (n == null || Number.isNaN(n)) return '—'
  return new Intl.NumberFormat().format(n)
}

function openCreateDialog() {
  editingVertical.value = null
  form.name = ''
  form.website_visitors = ''
  formDialogVisible.value = true
}

function openEditDialog(row) {
  editingVertical.value = row
  form.name = row.name
  form.website_visitors = row.website_visitors != null ? String(row.website_visitors) : ''
  formDialogVisible.value = true
}

function resetFormDialog() {
  editingVertical.value = null
  form.name = ''
  form.website_visitors = ''
}

async function submitForm() {
  const name = form.name?.trim()
  if (!name) {
    ElMessage.warning('Name is required')
    return
  }
  const website_visitors = form.website_visitors != null && form.website_visitors !== '' ? Number(form.website_visitors) : null
  saving.value = true
  try {
    if (editingVertical.value) {
      await verticals.update(editingVertical.value.id, { name, website_visitors })
      ElNotification.success({ message: 'Vertical updated' })
    } else {
      await verticals.create({ name, website_visitors })
      ElNotification.success({ message: 'Vertical added' })
    }
    formDialogVisible.value = false
    await verticals.fetchList()
  } catch (e) {
    ElNotification.error({ message: e?.message ?? 'Failed to save' })
  } finally {
    saving.value = false
  }
}

function confirmDelete(row) {
  verticalToDelete.value = row
  deleteDialogVisible.value = true
}

async function doDelete() {
  if (!verticalToDelete.value) return
  deletingId.value = verticalToDelete.value.id
  try {
    await verticals.remove(verticalToDelete.value.id)
    ElNotification.success({ message: 'Vertical deleted' })
    deleteDialogVisible.value = false
    verticalToDelete.value = null
    await verticals.fetchList()
    const filters = useFiltersStore()
    if (verticals.items.length === 1) {
      filters.vertical = verticals.items[0].name
    }
  } catch (e) {
    ElNotification.error({ message: e?.message ?? 'Failed to delete' })
  } finally {
    deletingId.value = null
  }
}

onMounted(() => verticals.fetchList())
</script>
