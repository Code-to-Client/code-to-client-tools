<template>
  <div
    class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50 p-6 shadow-sm"
  >
    <div class="text-base font-medium" :style="{ color: variantColor }">
      {{ label }}
    </div>
    <div class="mt-1 text-2xl font-semibold" style="color: var(--el-color-primary);">
      {{ value ?? 0 }}<span v-if="percentage" class="ml-1.5 text-sm font-normal text-gray-400">· {{ percentage }}</span>
    </div>
  </div>
</template>

<script setup>
import { STATUS_COLORS } from '~/stores/contacts'

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  value: {
    type: Number,
    default: 0,
  },
  percentage: {
    type: String,
    default: null,
  },
  variant: {
    type: String,
    default: 'CONTACTED',
    validator: (v) => ['CONTACTED', 'DESIGN_PARTNER_PROSPECT', 'WAITLISTED', 'OTHER_PROSPECT', 'DISCOVERY_CALL', 'DESIGN_PARTNER', 'CUSTOMER', 'NOT_INTERESTED'].includes(v),
  },
})

const variantColor = computed(() => STATUS_COLORS[props.variant] ?? STATUS_COLORS.CONTACTED)

</script>
