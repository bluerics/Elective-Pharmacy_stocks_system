
<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

withDefaults(
  defineProps<{
    collapsed?: boolean
  }>(),
  { collapsed: false },
)

const emit = defineEmits<{
  navigate: []
}>()

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const isAdmin = computed(() => auth.isAdmin)

const userName = computed(() => {
  const user = auth.user as {
    full_name?: string
    first_name?: string
    last_name?: string
    username?: string
  } | null | undefined

  return (
    user?.full_name ||
    [user?.first_name, user?.last_name].filter(Boolean).join(' ') ||
    user?.username ||
    'User'
  )
})

const menuItems = computed(() => {
  const items = [
    { label: 'Dashboard', path: '/dashboard', icon: 'dashboard' },
    { label: 'Medicines', path: '/medicines', icon: 'medicine' },
    { label: 'Suppliers', path: '/suppliers', icon: 'suppliers' },
    { label: 'Stocks', path: '/stocks', icon: 'stocks' },
    { label: 'Purchase Orders', path: '/purchase_orders', icon: 'orders' },
  ]

  if (isAdmin.value) {
    items.push({
      label: 'Accounts & Roles',
      path: '/accounts',
      icon: 'accounts',
    })
  }

  return items
})

function isActive(path: string) {
  return route.path === path || route.path.startsWith(path + '/')
}

async function handleLogout() {
  auth.logout()
  await router.replace('/login')
}
</script>

<template>
  <aside
    class="flex h-full min-h-0 shrink-0 flex-col overflow-hidden
           border-r border-white/10 bg-[#1A2D42] text-white
           transition-[width] duration-300"
    :class="collapsed ? 'w-20' : 'w-64'"
  >
    <!-- Logo -->
    <div
      class="shrink-0 border-b border-white/10 py-6"
      :class="collapsed ? 'px-3' : 'px-6'"
    >
      <div
        class="flex items-center gap-3"
        :class="collapsed ? 'justify-center' : ''"
      >
        <div
          class="flex h-10 w-10 shrink-0 items-center justify-center
                 rounded-xl bg-[#0AD1C8]/15 text-[#80ED99]"
          title="PharmaStock"
        >
          <svg
            class="h-6 w-6"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M10 3h4v5l4.5 7.5a3.5 3.5 0 0 1-3 5.5h-7a3.5 3.5 0 0 1-3-5.5L10 8V3Z" />
            <path d="M8 15h8" />
            <path d="M12 12v6" />
            <path d="M9 15h6" />
          </svg>
        </div>

        <div v-if="!collapsed" class="min-w-0">
          <h1 class="text-xl font-extrabold tracking-wide text-[#80ED99]">
            PharmaStock
          </h1>
          <p class="mt-1 text-xs text-slate-400">
            Pharmacy Inventory System
          </p>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <nav
      class="min-h-0 flex-1 space-y-2 overflow-y-auto px-3 py-6"
      aria-label="Main navigation"
    >
      <p
        v-if="!collapsed"
        class="mb-4 px-3 text-[10px] font-extrabold uppercase
               tracking-[0.2em] text-slate-400"
      >
        Main Menu
      </p>

      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        :title="collapsed ? item.label : undefined"
        class="group flex items-center gap-3 rounded-xl px-3 py-3
               text-sm font-semibold transition-all duration-200"
        :class="[
          isActive(item.path)
            ? 'bg-[#0AD1C8]/15 text-[#80ED99] shadow-sm shadow-black/10'
            : 'text-slate-300 hover:bg-white/[0.06] hover:text-white',
          collapsed ? 'justify-center' : '',
        ]"
        :aria-current="isActive(item.path) ? 'page' : undefined"
        @click="emit('navigate')"
      >
        <!-- Dashboard icon -->
        <svg
          v-if="item.icon === 'dashboard'"
          class="h-5 w-5 shrink-0"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <rect x="3" y="3" width="8" height="8" rx="2" />
          <rect x="13" y="3" width="8" height="5" rx="2" />
          <rect x="13" y="10" width="8" height="11" rx="2" />
          <rect x="3" y="13" width="8" height="8" rx="2" />
        </svg>

        <!-- Medicines icon -->
        <svg
          v-else-if="item.icon === 'medicine'"
          class="h-5 w-5 shrink-0"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="m10.5 20.5 10-10a5.66 5.66 0 0 0-8-8l-10 10a5.66 5.66 0 0 0 8 8Z" />
          <path d="m8.5 8.5 7 7" />
        </svg>

        <!-- Suppliers icon -->
        <svg
          v-else-if="item.icon === 'suppliers'"
          class="h-5 w-5 shrink-0"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M3 21h18" />
          <path d="M5 21V7l8-4v18" />
          <path d="M13 10h6v11" />
          <path d="M8 9h2M8 13h2M8 17h2" />
          <path d="M16 14h1M16 17h1" />
        </svg>

        <!-- Stocks icon -->
        <svg
          v-else-if="item.icon === 'stocks'"
          class="h-5 w-5 shrink-0"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="m12 3 9 5-9 5-9-5 9-5Z" />
          <path d="m3 12 9 5 9-5" />
          <path d="m3 16 9 5 9-5" />
        </svg>

        <!-- Purchase Orders icon -->
        <svg
          v-else-if="item.icon === 'orders'"
          class="h-5 w-5 shrink-0"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <circle cx="9" cy="21" r="1" />
          <circle cx="20" cy="21" r="1" />
          <path d="M1 1h4l2.7 13.4a2 2 0 0 0 2 1.6h9.7a2 2 0 0 0 2-1.6L23 6H6" />
          <path d="M12 8v5M9.5 10.5h5" />
        </svg>

        <!-- Accounts & Roles icon -->
        <svg
          v-else-if="item.icon === 'accounts'"
          class="h-5 w-5 shrink-0"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
          <circle cx="10" cy="7" r="4" />
          <path d="M20 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>

        <span
          v-if="!collapsed"
          class="min-w-0 flex-1 truncate"
        >
          {{ item.label }}
        </span>

        <span
          v-if="!collapsed && isActive(item.path)"
          class="h-1.5 w-1.5 shrink-0 rounded-full bg-[#80ED99]"
          aria-hidden="true"
        />
      </router-link>
    </nav>



      <button
        type="button"
        class="group flex w-full items-center gap-3 rounded-xl
               px-3 py-3 text-sm font-semibold text-rose-300
               transition-colors hover:bg-rose-500/10
               hover:text-rose-200"
        :class="collapsed ? 'justify-center' : ''"
        :title="collapsed ? 'Log Out' : undefined"
        @click="handleLogout"
      >
        <svg
          class="h-5 w-5 shrink-0 transition-transform
                 group-hover:translate-x-0.5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
          <path d="m16 17 5-5-5-5M21 12H9" />
        </svg>

        <span v-if="!collapsed">Log Out</span>
      </button>
  </aside>
</template>
