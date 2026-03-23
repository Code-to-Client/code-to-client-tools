<template>
  <div class="page-container">
    <NuxtRouteAnnouncer />
    <header class="nav-bar">
      <div class="nav-bar-inner">
      <NuxtLink to="/" class="flex items-center gap-2.5 shrink-0 no-underline group">
        <span
          class="app-logo flex h-9 w-9 items-center justify-center rounded-xl text-white text-sm font-bold shadow-md transition-transform group-hover:scale-105"
          aria-hidden
          :style="{ backgroundColor: primaryColor, boxShadow: `0 4px 6px -1px ${primaryColor}40, 0 2px 4px -2px ${primaryColor}40` }"
        >
          OT
        </span>
        <span class="logo-text text-lg font-semibold text-gray-800 dark:text-gray-100 tracking-tight transition-colors">
          Outreach Tracker
        </span>
      </NuxtLink>
      <nav class="nav-links flex-1">
        <NuxtLink to="/" class="nav-link" active-class="nav-link-active">Dashboard</NuxtLink>
        <NuxtLink to="/contacts" class="nav-link" active-class="nav-link-active">Contacts</NuxtLink>
        <NuxtLink to="/contacts/new" class="nav-link" active-class="nav-link-active">Add contact</NuxtLink>
        <NuxtLink to="/settings/verticals" class="nav-link" active-class="nav-link-active">Verticals</NuxtLink>
      </nav>
      <div class="flex items-center gap-3 shrink-0">
        <el-popover placement="bottom-end" :width="260" trigger="click">
          <template #default>
            <div class="flex flex-col gap-4 py-1">
              <div>
                <div class="mb-2 text-xs font-medium text-gray-500 dark:text-gray-400">Primary</div>
                <el-select
                  :model-value="primaryColor"
                  class="!w-full"
                  placeholder="Primary"
                  :teleported="false"
                  @update:model-value="setPrimary"
                >
                  <template #label="{ value }">
                    <span class="flex items-center gap-2">
                      <span
                        class="inline-block h-4 w-4 rounded-full border border-gray-300 dark:border-gray-600 shrink-0"
                        :style="{ backgroundColor: value }"
                      />
                      {{
                        primaryOptions.find((opt) => opt.value === value)?.label || 'Primary'
                      }}
                    </span>
                  </template>
                  <el-option
                    v-for="opt in primaryOptions"
                    :key="opt.value"
                    :label="opt.label"
                    :value="opt.value"
                  >
                    <span class="flex items-center gap-2">
                      <span
                        class="inline-block h-4 w-4 rounded-full border border-gray-300 dark:border-gray-600 shrink-0"
                        :style="{ backgroundColor: opt.value }"
                      />
                      {{ opt.label }}
                    </span>
                  </el-option>
                </el-select>
              </div>
              <div>
                <div class="mb-2 text-xs font-medium text-gray-500 dark:text-gray-400">Secondary</div>
                <el-select
                  :model-value="secondaryColor"
                  class="!w-full"
                  placeholder="Secondary"
                  :teleported="false"
                  @update:model-value="setSecondary"
                >
                  <template #label="{ value }">
                    <span class="flex items-center gap-2">
                      <span
                        class="inline-block h-4 w-4 rounded-full border border-gray-300 dark:border-gray-600 shrink-0"
                        :style="{ backgroundColor: value }"
                      />
                      {{
                        secondaryOptions.find((opt) => opt.value === value)?.label || 'Secondary'
                      }}
                    </span>
                  </template>
                  <el-option
                    v-for="opt in secondaryOptions"
                    :key="opt.value"
                    :label="opt.label"
                    :value="opt.value"
                  >
                    <span class="flex items-center gap-2">
                      <span
                        class="inline-block h-4 w-4 rounded-full border border-gray-300 dark:border-gray-600 shrink-0"
                        :style="{ backgroundColor: opt.value }"
                      />
                      {{ opt.label }}
                    </span>
                  </el-option>
                </el-select>
              </div>
            </div>
          </template>
          <template #reference>
            <el-button size="default" class="shrink-0">
              Colors
            </el-button>
          </template>
        </el-popover>
        <el-button
          circle
          :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          @click="toggle"
        >
          <el-icon>
            <Sunny v-if="isDark" />
            <Moon v-else />
          </el-icon>
        </el-button>
      </div>
      </div>
    </header>
    <main class="page-content">
      <NuxtPage />
    </main>
  </div>
</template>

<script setup>
import { Moon, Sunny } from '@element-plus/icons-vue'

const { isDark, toggle } = useDark()
const { primaryColor, setPrimary, options: primaryOptions } = usePrimaryColor()
const { secondaryColor, setSecondary, options: secondaryOptions } = useSecondaryColor()
</script>
