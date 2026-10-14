
<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterView } from 'vue-router'
import AppSidebar from '../components/AppSidebar.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const isMobile = ref(false)
const sidebarExpanded = ref(true)
const mobileSidebarOpen = ref(false)

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

const userRole = computed(() => auth.isAdmin ? 'Admin' : 'Staff')

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
}

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
    />

    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 z-50 transition-transform duration-300
             md:relative md:inset-auto md:translate-x-0"
      :class="[
        isMobile
          ? (mobileSidebarOpen ? 'translate-x-0' : '-translate-x-full')
          : '',
        !isMobile && sidebarExpanded ? 'w-64' : '',
        !isMobile && !sidebarExpanded ? 'w-20' : '',
      ]"
    >
      <AppSidebar
        :collapsed="!isMobile && !sidebarExpanded"
        @navigate="closeMobileSidebar"
      />
    </aside>

    <!-- Main content area -->
    <div class="flex min-w-0 min-h-0 flex-1 flex-col overflow-hidden">
      <!-- Header -->
      <header
        class="sticky top-0 z-30 flex h-24 items-center
               justify-between bg-gradient-to-br from-[#80ED99]/20
           via-[#0AD1C8]/10 to-[#213A57]/15 px-4 shadow-md sm:px-6"
      >
        <!-- Left: Toggle and branding -->
        <div class="flex min-w-0 items-center gap-3">
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

          <div class="min-w-0">
            <h3 class="truncate text-lg font-extrabold text-[#80ED99]">
              <p class="text-xs text-slate-300">
              Welcome back,
            </p>
            </h3>
            <p class="hidden text-xs text-slate-400 sm:block">
              Pharmacy Inventory System
            </p>
          </div>
        </div>

        <!-- Right: User information -->
        <div class="ml-3 flex shrink-0 items-center gap-3">
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
            class="flex h-10 w-10 shrink-0 items-center justify-center
                   rounded-full border border-[#0AD1C8]/30
                   bg-[#0AD1C8]/15 font-bold text-[#80ED99]"
            :title="`${userName} — ${userRole}`"
          >
            {{ userName.charAt(0).toUpperCase() }}
          </div>

          <!-- User information on mobile -->
          <div class="max-w-28 sm:hidden">
            <p class="truncate text-sm font-bold text-white">
              {{ userName }}
            </p>
            <p class="text-xs font-semibold text-[#0AD1C8]">
              {{ userRole }}
            </p>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main
        class="scrollbar-hide flex min-w-0 min-h-0 flex-1
               flex-col overflow-y-auto overflow-x-hidden p-4 sm:p-6"
      >
        <RouterView />
      </main>
    </div>
  </div>
</template>
