<template>
  <div class="flex flex-wrap items-center gap-3 shrink-0">
    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Vertical: </span>
    <span v-if="verticals.items.length === 1" class="text-sm font-semibold text-gray-800 dark:text-gray-100">
      {{ verticals.items[0].name }}
    </span>
    <el-select v-else v-model="filters.vertical" placeholder="All verticals" clearable class="!w-44">
      <el-option label="All verticals" value="" />
      <el-option v-for="v in verticals.items" :key="v.id" :label="v.name" :value="v.name" />
    </el-select>

    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Zip: </span>
    <el-select v-model="filters.zip" placeholder="All" clearable class="!w-28" @change="onZipChange">
      <el-option label="All" value="" />
      <el-option v-for="z in locations.zips" :key="z" :label="z" :value="z" />
    </el-select>

    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">City: </span>
    <el-select v-model="filters.cityState" placeholder="All" clearable class="!w-44" @change="onCityChange">
      <el-option label="All" value="" />
      <el-option v-for="cs in locations.cityStates" :key="cs" :label="cs" :value="cs" />
    </el-select>
  </div>
</template>

<script setup>
const filters = useFiltersStore()
const verticals = useVerticalsStore()
const locations = useLocationsStore()

function onZipChange(val) {
  if (val) filters.cityState = ''
}

function onCityChange(val) {
  if (val) filters.zip = ''
}

watch(() => filters.vertical, (vertical) => {
  filters.zip = ''
  filters.cityState = ''
  locations.fetchList(vertical || undefined)
})

onMounted(() => {
  verticals.fetchList()
  locations.fetchList(filters.vertical || undefined)
})
</script>
