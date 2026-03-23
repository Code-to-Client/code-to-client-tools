<template>
  <span
    class="inline-flex items-center rounded px-2 py-0.5 text-sm font-medium border"
    :style="{ color: tagColor, borderColor: tagColor }"
  >
    {{ label }}
  </span>
</template>

<script setup>
import { STATUS_LABELS, STATUS_COLORS } from '~/stores/contacts'

const props = defineProps(['status'])

const label = computed(() => STATUS_LABELS[props.status] || props.status)

const tagColor = computed(() => STATUS_COLORS[props.status] ?? STATUS_COLORS.contacted)
</script>
