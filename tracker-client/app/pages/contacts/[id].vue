<template>
  <div v-if="contact" class="max-w-4xl">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <h1 class="dashboard-title mb-1 text-2xl font-bold text-gray-800 dark:text-gray-100">
          Edit contact
          <span class="dashboard-title-underline block mt-1 h-0.5 w-12 rounded-full" />
        </h1>
        <span
          v-if="contact.contact_source === 'MANUAL'"
          class="rounded px-2 py-0.5 text-xs font-medium bg-gray-200 text-gray-700 dark:bg-gray-600 dark:text-gray-300"
        >
          Added manually
        </span>
      </div>
      <!-- <StatusBadge :status="contact.status" /> -->
    </div>

    <div class="flex gap-6">
      <div class="flex-1 min-w-0">
        <div class="card card-body">
          <el-form :model="form" label-width="140px">
            <el-form-item label="Vertical">
              <el-select
                v-model="form.vertical"
                class="w-full"
                placeholder="Select vertical"
                clearable
                filterable
                allow-create
                default-first-option
              >
                <el-option
                  v-for="v in verticalsList"
                  :key="v.id"
                  :label="v.name"
                  :value="v.name"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Contact page URL">
              <el-input v-model="form.contact_url" placeholder="https://..." />
            </el-form-item>

            <el-form-item label="Status">
              <div class="status-select-wrapper w-full" :style="{ color: STATUS_COLORS[form.status] }">
              <el-select
                v-model="form.status"
                class="w-full"
              >
                <el-option
                  v-for="(label, key) in STATUS_LABELS"
                  :key="key"
                  :label="label"
                  :value="key"
                />
              </el-select>
              </div>
            </el-form-item>

            <el-form-item label="Contact name">
              <el-input v-model="form.contact_name" placeholder="Person's name" />
            </el-form-item>

            <el-form-item label="Company name">
              <el-input v-model="form.company_name" />
            </el-form-item>

            <div class="form-row-2">
              <div>
                <div class="form-field-label">Email</div>
                <el-input v-model="form.email" type="email" placeholder="email@example.com" />
              </div>
              <div>
                <div class="form-field-label">Phone</div>
                <el-input v-model="form.phone" placeholder="+1 234 567 8900" />
              </div>
            </div>
            <div class="form-row-3">
              <div>
                <div class="form-field-label">City</div>
                <el-input v-model="form.city" />
              </div>
              <div>
                <div class="form-field-label">State</div>
                <el-input v-model="form.state" />
              </div>
              <div>
                <div class="form-field-label">Zip code</div>
                <el-input v-model="form.postal_code" />
              </div>
            </div>

            <el-form-item label="Main website URL">
              <el-input
                v-model="form.url"
                placeholder="https://..."
                @focus="onMainUrlFocus"
              />
            </el-form-item> 

            <el-form-item label="Contacted date">
              <el-input v-model="form.contacted_at" disabled />
            </el-form-item>

            <el-form-item>
              <template #label>
                <span class="inline-flex items-center gap-1.5">
                  Notes
                </span>
              </template>
              <el-input v-model="form.notes" type="textarea" @click="showNotesDialog = true" :rows="4" readonly />
            </el-form-item>

            <el-form-item label="Next action">
              <el-input v-model="form.next_action" />
            </el-form-item>

            <el-form-item class="!justify-end">
              <div class="flex justify-end gap-3 w-full">
                <el-button type="danger" :loading="deleting" @click="confirmDelete">
                  Delete
                </el-button>
                <NuxtLink to="/contacts">
                  <el-button>Cancel</el-button>
                </NuxtLink>
                <el-button type="primary" :loading="saving" @click="save">
                  Save
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <div v-if="contact.status_history?.length" class="w-72 shrink-0">
        <div class="card card-body">
          <StatusHistory :history="contact.status_history" />
        </div>
      </div>
    </div>
  </div>

  <div v-else class="card card-body">
    <p class="text-gray-500">Loading...</p>
  </div>

  <el-dialog
    v-model="showNotesDialog"
    title="Edit Notes"
    width="560px"
    @opened="onNotesDialogOpened"
  >
    <el-input
      ref="notesInputRef"
      v-model="form.notes"
      type="textarea"
      :rows="25"
      placeholder="No notes"
      class="!font-mono"
    />
    <template #footer>
      <el-button @click="prependNotesDate">Add Note</el-button>
      <el-button @click="showNotesDialog = false">Close</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="showDeleteConfirm" title="Delete contact" width="400px">
    <p>Are you sure you want to delete this contact?</p>
    <template #footer>
      <el-button @click="showDeleteConfirm = false">Cancel</el-button>
      <el-button type="danger" :loading="deleting" @click="doDelete">Delete</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { STATUS_LABELS, STATUS_COLORS } from '~/stores/contacts'

const route = useRoute()
const router = useRouter()
const contacts = useContactsStore()
const verticals = useVerticalsStore()
const id = computed(() => Number(route.params.id))

const verticalsList = computed(() => verticals.items || [])

const contact = ref(null)
const notesInputRef = ref()

const form = reactive({
  contact_name: '',
  company_name: '',
  email: '',
  phone: '',
  city: '',
  state: '',
  postal_code: '',
  url: '',
  contact_url: '',
  vertical: '',
  contacted_at: '',
  status: '',
  notes: '',
  next_action: '',
})

const saving = ref(false)
const deleting = ref(false)
const showDeleteConfirm = ref(false)
const showNotesDialog = ref(false)

function inferMainUrlFromContactUrl(contactUrl) {
  if (!contactUrl || typeof contactUrl !== 'string') return ''
  const trimmed = contactUrl.trim()
  if (!trimmed) return ''
  try {
    const u = new URL(trimmed)
    return u.origin
  } catch {
    return ''
  }
}

function onMainUrlFocus() {
  if (!form.url?.trim() && form.contact_url?.trim()) {
    const inferred = inferMainUrlFromContactUrl(form.contact_url)
    if (inferred) form.url = inferred
  }
}

function prependNotesDate() {
  const d = new Date()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const yyyy = d.getFullYear()
  const stamp = `${mm}/${dd}/${yyyy}`
  const prefix = `${stamp}\n\n\n`
  form.notes = prefix + (form.notes || '')

  nextTick(() => {
    const inputEl = notesInputRef.value?.textarea || notesInputRef.value?.input
    if (inputEl) {
      // Place cursor on the first blank line after the date
      const pos = prefix.length - 1
      inputEl.focus()
      inputEl.setSelectionRange(pos, pos - 1)
      inputEl.scrollTop = 0
    }
  })
}

function onNotesDialogOpened() {
  nextTick(() => {
    const inputEl = notesInputRef.value?.textarea || notesInputRef.value?.input
    if (inputEl) {
      inputEl.scrollTop = 0
    }
  })
}


onMounted(async () => {
  await verticals.fetchList()
  try {
    contact.value = await contacts.fetchOne(id.value)
  } catch (e) {
    ElNotification.error({ message: 'Contact not found. It may have been deleted.' })
    router.push('/contacts')
    return
  }

  if (contact.value) {
    form.contact_name = contact.value.contact_name || ''
    form.company_name = contact.value.company_name || ''
    form.email = contact.value.email || ''
    form.phone = contact.value.phone || ''
    form.city = contact.value.city || ''
    form.state = contact.value.state || ''
    form.postal_code = contact.value.postal_code || ''
    form.url = contact.value.url || ''
    form.contact_url = contact.value.contact_url || ''
    form.vertical = contact.value.vertical || ''
    form.contacted_at = contact.value.contacted_at || ''
    form.status = contact.value.status
    form.notes = contact.value.notes || ''
    form.next_action = contact.value.next_action || ''
  }
})

async function save() {
  saving.value = true
  try {
    await contacts.update(id.value, {
      contact_name: form.contact_name?.trim() || undefined,
      company_name: form.company_name?.trim() ?? '',
      email: form.email?.trim() || undefined,
      phone: form.phone?.trim() || undefined,
      city: form.city?.trim() || undefined,
      state: form.state?.trim() || undefined,
      postal_code: form.postal_code?.trim() || undefined,
      url: form.url || undefined,
      contact_url: form.contact_url || undefined,
      vertical: form.vertical || undefined,
      contacted_at: form.contacted_at || undefined,
      status: form.status,
      notes: form.notes || undefined,
      next_action: form.next_action || undefined,
    })
    contact.value = await contacts.fetchOne(id.value)
    ElNotification.success({ message: 'Changes Saved' })
  } catch (e) {
    ElNotification.error({ message: e?.message ?? 'Failed to save' })
  } finally {
    saving.value = false
  }
}

function confirmDelete() {
  showDeleteConfirm.value = true
}

async function doDelete() {
  deleting.value = true
  try {
    await contacts.remove(id.value)
    ElNotification.success({ message: 'Deleted' })
    router.push('/contacts')
  } catch (e) {
    ElNotification.error({ message: e?.message ?? 'Failed to delete' })
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.status-select-wrapper :deep(.el-input__inner),
.status-select-wrapper :deep(.el-select__selected-item),
.status-select-wrapper :deep(.el-select__placeholder) {
  color: inherit !important;
}
.form-row-2,
.form-row-3 {
  margin-left: 140px;
  margin-bottom: 18px;
}
.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 12px;
}
.form-row-3 {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 0 12px;
}
.form-field-label {
  font-size: 14px;
  color: var(--el-text-color-regular);
  margin-bottom: 4px;
}
</style>
