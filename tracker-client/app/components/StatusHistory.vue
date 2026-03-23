<template>
  <div>
    <div class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 border-l-2 border-primary pl-2">Status history</div>
    <el-timeline v-if="entries.length">
      <el-timeline-item
        v-for="(entry, i) in entries"
        :key="i"
        :timestamp="formatDate(entry.changed_at || entry.date)"
        :color="statusColor(entry.status)"
        placement="top"
        size="large"
      >
        <StatusBadge :status="entry.status" />
      </el-timeline-item>
    </el-timeline>
    <p v-else class="text-sm text-gray-400 dark:text-gray-500">No status history</p>
  </div>
</template>

<script setup>
import { STATUS_COLORS } from '~/stores/contacts'

const props = defineProps({
  history: {
    type: Array,
    default: () => [],
  },
})

const entries = computed(() => {
  if (!Array.isArray(props.history) || props.history.length === 0) return []
  return [...props.history].sort((a, b) => {
    const dA = a.changed_at || a.date || ''
    const dB = b.changed_at || b.date || ''
    return dB.localeCompare(dA)
  })
})

function formatDate(value) {
  if (!value) return '—'
  const s = typeof value === 'string' ? value : value.toISOString?.() ?? String(value)
  return s.slice(0, 10)
}

function statusColor(status) {
  return STATUS_COLORS[status] ?? STATUS_COLORS.CONTACTED
}
</script>
