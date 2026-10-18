
<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import AppSidebar from '../components/AppSidebar.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

// Page title
const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    Dashboard: 'Welcome Back',
    Medicines: 'Medicine Management',
    Stocks: 'Inventory Management',
    PurchaseOrders: 'Purchase Order Management',
    Suppliers: 'Supplier Management',
    Accounts: 'User Management',
  }

  return titles[String(route.name)] || 'Pharmacy Inventory System'
})

const isDashboard = computed(() => route.name === 'Dashboard')

// Navigation
function goToDashboard() {
  router.push('/dashboard')
}

// Sidebar
const isMobile = ref(false)
const sidebarExpanded = ref(true)
const mobileSidebarOpen = ref(false)

// Profile dropdown
const profileMenuOpen = ref(false)

function toggleProfileMenu() {
  profileMenuOpen.value = !profileMenuOpen.value
}

function closeProfileMenu() {
  profileMenuOpen.value = false
}

// User information
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

const userRole = computed(() => (auth.isAdmin ? 'Admin' : 'Staff'))

// Logout
function handleLogout() {
  closeProfileMenu()
  auth.logout()
  router.push('/login')
}

// Screen size
function checkScreenSize() {
  isMobile.value = window.innerWidth < 768

  if (!isMobile.value) {
    mobileSidebarOpen.value = false
  }
}

function toggleSidebar() {
  if (isMobile.value) {
    mobileSidebarOpen.value = !mobileSidebarOpen.value
  } else {
    sidebarExpanded.value = !sidebarExpanded.value
  }
}

function closeMobileSidebar() {
  if (isMobile.value) {
    mobileSidebarOpen.value = false
  }

  closeProfileMenu()
}

// Lifecycle
onMounted(() => {
  auth.restoreSession()
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})
</script>

<template>
  <div
    class="flex h-screen overflow-hidden
           bg-gradient-to-br from-[#80ED99]/20
           via-[#0AD1C8]/10 to-[#213A57]/15"
  >
    <!-- Mobile backdrop -->
    <div
      v-if="isMobile && mobileSidebarOpen"
      class="fixed inset-0 z-40 bg-black/50 md:hidden"
      @click="closeMobileSidebar"
    ></div>

    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 z-50
             transition-all duration-300
             md:relative md:inset-auto md:translate-x-0"
      :class="[
        isMobile
          ? (mobileSidebarOpen
              ? 'translate-x-0 w-64'
              : '-translate-x-full w-64')
          : (sidebarExpanded ? 'w-64' : 'w-20'),
      ]"
    >
      <AppSidebar
        :collapsed="!isMobile && !sidebarExpanded"
        @navigate="closeMobileSidebar"
      />
    </aside>

    <!-- Main content -->
    <div class="flex min-w-0 min-h-0 flex-1 flex-col overflow-hidden">
      <!-- Header -->
      <header
        class="sticky top-0 z-30 flex h-24 shrink-0 items-center
               justify-between gap-3
               bg-gradient-to-br from-[#80ED99]/20
               via-[#0AD1C8]/10 to-[#213A57]/15
               px-4 shadow-md sm:px-6"
      >
        <!-- Left: Sidebar toggle and page title -->
        <div class="flex min-w-0 items-center gap-2 sm:gap-3">
          <button
            type="button"
            class="flex h-10 w-10 shrink-0 items-center justify-center
                   rounded-xl text-xl text-[#80ED99]
                   transition hover:bg-white/10"
            :aria-label="isMobile ? 'Open navigation' : 'Toggle sidebar'"
            :aria-expanded="isMobile ? mobileSidebarOpen : sidebarExpanded"
            @click="toggleSidebar"
          >
            <span aria-hidden="true">
              {{ isMobile ? '☰' : sidebarExpanded ? '◧' : '☰' }}
            </span>
          </button>

          <!-- Back arrow and page title -->
          <div class="flex min-w-0 items-center gap-2 sm:gap-3">
            <button
              v-if="!isDashboard"
              type="button"
              @click="goToDashboard"
              class="flex h-10 w-10 shrink-0 items-center justify-center
                     rounded-xl text-2xl font-bold text-white
                     transition hover:bg-white/10 hover:text-[#80ED99]"
              aria-label="Back to Dashboard"
              title="Back to Dashboard"
            >
              ←
            </button>

            <div class="min-w-0">
              <h1
                class="truncate text-lg font-extrabold text-white
                       sm:text-3xl lg:text-4xl"
              >
                {{ pageTitle }}
              </h1>

              <p class="text-xs text-white">
                Pharmacy Inventory System
              </p>
            </div>
          </div>
        </div>

        <!-- Right: Clickable profile -->
        <div class="relative ml-2 shrink-0">
          <button
            type="button"
            @click="toggleProfileMenu"
            class="flex items-center gap-2 rounded-xl p-2
                   transition hover:bg-white/10
                   focus:outline-none focus:ring-2 focus:ring-[#0AD1C8]
                   sm:gap-3"
            :aria-expanded="profileMenuOpen"
            aria-label="Open profile menu"
          >
            <!-- Desktop user information -->
            <div class="hidden text-right sm:block">
              <p class="max-w-48 truncate text-sm font-bold text-white">
                {{ userName }}
              </p>

              <p class="text-xs font-semibold text-[#0AD1C8]">
                {{ userRole }}
              </p>
            </div>

            <!-- Avatar -->
            <div
              class="flex h-11 w-11 shrink-0 items-center justify-center
                     rounded-full border border-[#0AD1C8]/40
                     bg-[#0AD1C8]/15 text-lg font-bold text-[#80ED99]"
            >
              {{ userName.charAt(0).toUpperCase() }}
            </div>

            <span
              class="text-xs text-white transition-transform"
              :class="profileMenuOpen ? 'rotate-180' : ''"
            >
              ▼
            </span>
          </button>

          <!-- Profile dropdown -->
          <div
            v-if="profileMenuOpen"
            class="absolute right-0 top-full z-50 mt-3
                   w-72 max-w-[calc(100vw-2rem)]
                   overflow-hidden rounded-2xl
                   border border-white/10 bg-[#213A57]
                   shadow-2xl"
          >
            <!-- Profile heading -->
            <div
              class="border-b border-white/10
                     bg-gradient-to-r from-[#0AD1C8]/15
                     to-[#80ED99]/10 p-5"
            >
              <div class="flex items-center gap-3">
                <div
                  class="flex h-14 w-14 shrink-0 items-center justify-center
                         rounded-full border border-[#0AD1C8]/40
                         bg-[#0AD1C8]/15 text-2xl font-bold text-[#80ED99]"
                >
                  {{ userName.charAt(0).toUpperCase() }}
                </div>

                <div class="min-w-0">
                  <h3 class="truncate font-bold text-white">
                    {{ userName }}
                  </h3>

                  <p class="text-sm text-[#0AD1C8]">
                    {{ userRole }}
                  </p>

                  <p class="text-xs text-gray-300">
                    Pharmacy Inventory System
                  </p>
                </div>
              </div>
            </div>

            <!-- Profile details -->
            <div class="space-y-4 p-5">
              <div>
                <p class="text-xs font-medium uppercase tracking-wider text-gray-400">
                  Full Name
                </p>
                <p class="mt-1 break-words text-sm font-semibold text-white">
                  {{ auth.user?.full_name || 'Not provided' }}
                </p>
              </div>

              <div>
                <p class="text-xs font-medium uppercase tracking-wider text-gray-400">
                  Username
                </p>
                <p class="mt-1 break-words text-sm font-semibold text-white">
                  {{ auth.user?.username || 'Not provided' }}
                </p>
              </div>

              <div>
                <p class="text-xs font-medium uppercase tracking-wider text-gray-400">
                  Account ID
                </p>
                <p class="mt-1 text-sm font-semibold text-white">
                  {{ auth.user?.id ?? 'Not available' }}
                </p>
              </div>

              <div>
                <p class="text-xs font-medium uppercase tracking-wider text-gray-400">
                  Account Role
                </p>

                <span
                  class="mt-2 inline-flex rounded-full
                         bg-[#0AD1C8]/15 px-3 py-1
                         text-xs font-bold text-[#80ED99]"
                >
                  {{ userRole }}
                </span>
              </div>
            </div>

            <!-- Logout -->
            <div class="border-t border-white/10 p-3">
              <button
                type="button"
                @click="handleLogout"
                class="flex w-full items-center gap-3 rounded-xl
                       px-4 py-3 text-left text-sm font-semibold
                       text-red-300 transition hover:bg-red-500/10
                       hover:text-red-200"
              >
                <span aria-hidden="true">↪</span>
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main
        class="scrollbar-hide flex min-w-0 min-h-0 flex-1
               flex-col overflow-x-hidden overflow-y-auto"
      >
        <div class="min-h-full w-full p-4 sm:p-6">
          <RouterView />
        </div>
      </main>
    </div>
  </div>
</template>
