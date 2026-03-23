<template>
  <div>
    <h1 class="dashboard-title mb-1 text-2xl font-bold text-gray-800 dark:text-gray-100">
      Add contact
      <span class="dashboard-title-underline block mt-1 h-0.5 w-12 rounded-full" />
    </h1>
    <p class="mt-1 mb-8 text-sm text-gray-500 dark:text-gray-400">Create a new outreach contact.</p>

    <div class="card card-body max-w-xl">
      <el-form :model="form" label-width="140px">
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
      <el-form-item label="Contact page URL">
        <el-input v-model="form.contact_url" placeholder="https://..." />
      </el-form-item>
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
      <el-form-item label="Contacted date">
        <el-date-picker
          v-model="form.contacted_at"
          type="date"
          placeholder="Today"
          value-format="YYYY-MM-DD"
          class="w-full"
        />
      </el-form-item>
      <el-form-item label="Notes">
        <el-input v-model="form.notes" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item label="Next action">
        <el-input v-model="form.next_action" placeholder="e.g. Email follow-up on Friday" />
      </el-form-item>
      <el-form-item class="!justify-end">
        <div class="flex justify-end gap-3 w-full">
          <NuxtLink to="/contacts">
            <el-button>Cancel</el-button>
          <el-button type="primary" :loading="saving" @click="save" :disabled="!form.vertical">Save</el-button>
          </NuxtLink>
        </div>
      </el-form-item>
    </el-form>
    </div>
  </div>
</template>

<script setup>
const contacts = useContactsStore()
const verticals = useVerticalsStore()
const router = useRouter()
const saving = ref(false)

const verticalsList = computed(() => verticals.items || [])

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
  contacted_at: new Date().toLocaleDateString('en-CA'),
  status: 'CONTACTED',
  notes: '',
  next_action: '',
})

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

onMounted(async () => {
  await verticals.fetchList()
  if (!form.vertical && verticals.items?.length) {
    form.vertical = verticals.items[0].name
  }
})

async function save() {
  saving.value = true
  try {
    const c = await contacts.create({
      company_name: form.company_name?.trim() ?? '',
      contact_name: form.contact_name?.trim() || undefined,
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
    ElNotification.success({ message: 'Contact Added' })
    router.push(`/contacts/${c.id}`)
  } catch (e) {
    ElNotification.error({ message: e?.message ?? 'Failed to save' })
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
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
