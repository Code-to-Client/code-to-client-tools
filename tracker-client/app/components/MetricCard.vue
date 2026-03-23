<template>
  <el-card shadow="hover" class="metric-card-accent p-3">
    <div class="metric-value text-2xl font-bold">{{ value }}<span v-if="percentage" class="ml-1.5 text-lg font-normal text-gray-600">  ({{ percentage }})</span></div>
    <div class="mt-1 text-base text-gray-500 dark:text-gray-400">{{ label }}</div>
  </el-card>
</template>

<script setup>
defineProps(['label', 'value', 'percentage'])
</script>
