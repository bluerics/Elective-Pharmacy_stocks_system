
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const loading = ref(true)
const error = ref('')

const medicines = ref<Record<string, any>[]>([])
const stocks = ref<Record<string, any>[]>([])
const orders = ref<Record<string, any>[]>([])
const suppliers = ref<Record<string, any>[]>([])

function recordsFrom(data: any): Record<string, any>[] {
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.results)) return data.results
  return []
}

// Dashboard counts
const counts = computed(() => ({
  medicines: medicines.value.length,
  stocks: stocks.value.length,
  orders: orders.value.length,
  suppliers: suppliers.value.length,
}))

// Total units across ALL stock records
const totalStockUnits = computed(() =>
  stocks.value.reduce(
    (total, item) =>
      total + Number(item.quantity_available ?? item.quantity ?? 0),
    0,
  ),
)

// Get the medicine ID from a stock record.
// Supports Django foreign keys returned as IDs or nested objects.
function getMedicineId(item: Record<string, any>): string {
  const medicine = item.medicine ?? item.medicine_id

  if (medicine && typeof medicine === 'object') {
    return String(medicine.id ?? medicine.pk ?? '')
  }

  return String(medicine ?? '')
}

// Calculate the combined stock quantity for one medicine
function getStockQty(medicineId: number | string): number {
  return stocks.value
    .filter(
      (item) => getMedicineId(item) === String(medicineId),
    )
    .reduce(
      (total, item) =>
        total + Number(item.quantity_available ?? item.quantity ?? 0),
      0,
    )
}

// Get the reorder threshold from the medicine or its stock records
function getReorderLevel(medicine: Record<string, any>): number | null {
  if (
    medicine.reorder_level !== null &&
    medicine.reorder_level !== undefined &&
    medicine.reorder_level !== ''
  ) {
    return Number(medicine.reorder_level)
  }

  const relatedStocks = stocks.value.filter(
    (item) => getMedicineId(item) === String(medicine.id),
  )

  const stockWithReorderLevel = relatedStocks.find(
    (item) =>
      item.reorder_level !== null &&
      item.reorder_level !== undefined &&
      item.reorder_level !== '',
  )

  if (stockWithReorderLevel) {
    return Number(stockWithReorderLevel.reorder_level)
  }

  return null
}

// Medicines that have reached their configured reorder level
const lowStockMedicines = computed(() =>
  medicines.value.filter((medicine) => {
    const reorderLevel = getReorderLevel(medicine)

    if (reorderLevel === null || !Number.isFinite(reorderLevel)) {
      return false
    }

    return getStockQty(medicine.id) <= reorderLevel
  }),
)

// Most recent orders (assuming the API returns newest first)
const recentOrders = computed(() => orders.value.slice(0, 5))

// Load dashboard data from Django REST Framework
onMounted(async () => {
  loading.value = true
  error.value = ''

  try {
    const results = await Promise.allSettled([
      api.get('/medicines/'),
      api.get('/stocks/'),
      api.get('/purchase_orders/'),
      api.get('/suppliers/'),
    ])

    const [medicineResult, stockResult, orderResult, supplierResult] =
      results

    if (medicineResult.status === 'fulfilled') {
      medicines.value = recordsFrom(medicineResult.value.data)
    }

    if (stockResult.status === 'fulfilled') {
      stocks.value = recordsFrom(stockResult.value.data)
    }

    if (orderResult.status === 'fulfilled') {
      orders.value = recordsFrom(orderResult.value.data)
    }

    if (supplierResult.status === 'fulfilled') {
      suppliers.value = recordsFrom(supplierResult.value.data)
    }

    const failedRequests = results.filter(
      (result) => result.status === 'rejected',
    )

    if (failedRequests.length === results.length) {
      error.value =
        'Could not connect to the inventory API. Check that Django is running and your API URLs are correct.'
    } else if (failedRequests.length > 0) {
      error.value =
        'Some dashboard information could not be loaded. Check the Django API endpoints.'
    }
  } catch {
    error.value = 'An unexpected error occurred while loading the dashboard.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="space-y-6 overflow-y-auto w-full pb-6">

    <!-- Loading state -->
    <div
      v-if="loading"
      class="bg-white rounded-3xl border border-slate-200 p-10 text-center text-slate-500"
    >
      Loading dashboard...
    </div>

    <template v-else>
      <!-- API error message -->
      <div
        v-if="error"
        class="bg-amber-50 border border-amber-200 text-amber-800 p-4 rounded-2xl text-sm"
      >
        {{ error }}
      </div>

      <!-- Dashboard metric cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">

        <!-- Total Medicines -->
        <div
          class="bg-gradient-to-br from-[#213A57] to-[#0B6477] p-6 rounded-3xl shadow-lg text-white flex items-center justify-between relative overflow-hidden"
        >
          <div
            class="absolute right-0 top-0 w-24 h-24 bg-white/5 rounded-bl-full pointer-events-none"
          ></div>

          <div class="space-y-2 relative z-10">
            <span
              class="text-xs font-bold text-slate-300 uppercase tracking-wider block"
            >
              Total Medicines
            </span>

            <div class="text-3xl font-extrabold">
              {{ counts.medicines }}
            </div>

            <span
              class="inline-flex items-center space-x-1 text-[11px] font-bold text-[#213A57] bg-[#80ED99] px-2.5 py-0.5 rounded-full"
            >
              <i class="fa-solid fa-circle-dot text-[8px]"></i>
              <span>Active Catalog</span>
            </span>
          </div>

          <div
            class="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center backdrop-blur-md border border-white/20 relative z-10"
          >
            <svg
              class="w-7 h-7"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M19.428 15.428a2 2 0 00-2.856 2.856l2.856 2.856a2 2 0 102.856-2.856l-2.856-2.856zM12.5 12.5l-8.793 8.793a1 1 0 01-1.414-1.414l8.793-8.793M15 5.5a3.5 3.5 0 11-7 0 3.5 3.5 0 017 0z"
              />
            </svg>
          </div>
        </div>

        <!-- Total Stock Available -->
        <div
          class="bg-gradient-to-br from-[#0B6477] to-[#14919B] p-6 rounded-3xl shadow-lg text-white flex items-center justify-between relative overflow-hidden"
        >
          <div
            class="absolute right-0 top-0 w-24 h-24 bg-white/5 rounded-bl-full pointer-events-none"
          ></div>

          <div class="space-y-2 relative z-10">
            <span
              class="text-xs font-bold text-slate-200 uppercase tracking-wider block"
            >
              Total Stock Available
            </span>

            <div class="text-3xl font-extrabold">
              {{ totalStockUnits }}
            </div>

            <span
              class="inline-flex items-center space-x-1 text-[11px] font-bold text-[#213A57] bg-[#0AD1C8] px-2.5 py-0.5 rounded-full"
            >
              <i class="fa-solid fa-arrow-trend-up text-[8px]"></i>
              <span>In Inventory</span>
            </span>
          </div>

          <div
            class="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center backdrop-blur-md border border-white/20 relative z-10"
          >
            <svg
              class="w-7 h-7"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
              />
            </svg>
          </div>
        </div>

        <!-- Low Stock Items -->
        <div
          class="bg-gradient-to-br from-[#14919B] to-[#0AD1C8] p-6 rounded-3xl shadow-lg text-white flex items-center justify-between relative overflow-hidden"
        >
          <div
            class="absolute right-0 top-0 w-24 h-24 bg-white/5 rounded-bl-full pointer-events-none"
          ></div>

          <div class="space-y-2 relative z-10">
            <span
              class="text-xs font-bold text-slate-100 uppercase tracking-wider block"
            >
              Low Stock Items
            </span>

            <div class="text-3xl font-extrabold">
              {{ lowStockMedicines.length }}
            </div>

            <span
              class="inline-flex items-center space-x-1 text-[11px] font-bold text-white bg-[#213A57] px-2.5 py-0.5 rounded-full"
            >
              <i class="fa-solid fa-triangle-exclamation text-[8px]"></i>
              <span>Action Needed</span>
            </span>
          </div>

          <div
            class="w-14 h-14 rounded-2xl bg-white/20 flex items-center justify-center backdrop-blur-md border border-white/30 relative z-10"
          >
            <svg
              class="w-7 h-7"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
        </div>

        <!-- Registered Suppliers -->
        <div
          class="bg-gradient-to-br from-[#0B6477] via-[#14919B] to-[#45DFB1] p-6 rounded-3xl shadow-lg text-white flex items-center justify-between relative overflow-hidden"
        >
          <div
            class="absolute right-0 top-0 w-24 h-24 bg-white/5 rounded-bl-full pointer-events-none"
          ></div>

          <div class="space-y-2 relative z-10">
            <span
              class="text-xs font-bold text-slate-100 uppercase tracking-wider block"
            >
              Suppliers
            </span>

            <div class="text-3xl font-extrabold">
              {{ counts.suppliers }}
            </div>

            <span
              class="inline-flex items-center space-x-1 text-[11px] font-bold text-[#213A57] bg-[#80ED99] px-2.5 py-0.5 rounded-full"
            >
              <i class="fa-solid fa-truck-fast text-[8px]"></i>
              <span>Registered Vendors</span>
            </span>
          </div>

          <div
            class="w-14 h-14 rounded-2xl bg-white/20 flex items-center justify-center backdrop-blur-md border border-white/30 relative z-10"
          >
            <svg
              class="w-7 h-7"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0zM13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0"
              />
            </svg>
          </div>
        </div>
      </div>

      <!-- Low Stock & Reorder Alerts -->
      <div
        class="bg-white border border-slate-200/80 rounded-3xl p-6 shadow-sm space-y-4"
      >
        <div
          class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-4 border-b border-slate-100"
        >
          <div>
            <h2 class="text-base font-bold text-[#213A57]">
              Low Stock &amp; Reorder Alerts
            </h2>
            <p class="text-xs text-slate-400">
              Items requiring restock attention
            </p>
          </div>

          <button
            @click="router.push('/medicines')"
            class="text-xs font-bold text-[#14919B] hover:text-[#0B6477] flex items-center space-x-1 bg-slate-50 hover:bg-slate-100 px-3.5 py-2 rounded-xl transition-all"
          >
            <span>View Catalog</span>
            <i class="fa-solid fa-arrow-right text-[10px]"></i>
          </button>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead
              class="bg-slate-50/80 text-slate-500 uppercase text-[10px] font-extrabold tracking-wider border-b border-slate-100"
            >
              <tr>
                <th class="p-4">Medicine Name</th>
                <th class="p-4">Category</th>
                <th class="p-4">Current Stock</th>
                <th class="p-4">Reorder Level</th>
                <th class="p-4 text-right">Action</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-slate-100">
              <tr
                v-for="med in lowStockMedicines"
                :key="med.id"
                class="hover:bg-slate-50/60 transition-colors"
              >
                <td class="p-4 font-bold text-slate-800">
                  <span>{{ med.medicine_name ?? med.name ?? 'Unknown Medicine' }}</span>
                  <span class="text-xs text-slate-400 font-normal block">
                    ({{ med.brand_name ?? 'No brand specified' }})
                  </span>
                </td>

                <td class="p-4 text-slate-600">
                  <span
                    class="px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold"
                  >
                    {{ med.category ?? 'Uncategorized' }}
                  </span>
                </td>

                <td class="p-4 font-extrabold text-[#0B6477]">
                  {{ getStockQty(med.id) }} units
                </td>

                <td class="p-4 text-slate-600 font-semibold">
                  {{ getReorderLevel(med) }} units
                </td>

                <td class="p-4 text-right">
                  <button
                    @click="router.push('/purchase_orders')"
                    class="bg-gradient-to-r from-[#0B6477] to-[#14919B] hover:opacity-90 text-white px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-md"
                  >
                    Reorder Now
                  </button>
                </td>
              </tr>

              <tr v-if="lowStockMedicines.length === 0">
                <td colspan="5" class="p-12 text-center text-slate-400">
                  <div
                    class="flex flex-col items-center justify-center space-y-2"
                  >
                    <div
                      class="w-12 h-12 rounded-2xl bg-[#45DFB1]/30 text-[#0B6477] flex items-center justify-center text-lg border border-[#45DFB1]/40"
                    >
                      <i class="fa-solid fa-shield-halved"></i>
                    </div>

                    <span class="font-bold text-slate-700">
                      No low-stock items found
                    </span>

                    <span class="text-slate-400 text-xs">
                      Medicines with a configured reorder level will appear here
                      when their stock reaches that level.
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Recent Purchase Orders -->
      <div
        class="bg-white border border-slate-200/80 rounded-3xl p-6 shadow-sm space-y-4"
      >
        <div class="flex items-center justify-between pb-4 border-b border-slate-100">
          <div>
            <h2 class="text-base font-bold text-[#213A57]">
              Recent Purchase Orders
            </h2>
            <p class="text-xs text-slate-400">
              Your latest purchase orders
            </p>
          </div>

          <button
            @click="router.push('/purchase_orders')"
            class="text-xs font-bold text-[#14919B] hover:text-[#0B6477] bg-slate-50 px-3.5 py-2 rounded-xl"
          >
            View All
          </button>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead
              class="bg-slate-50 text-slate-500 uppercase text-[10px] font-extrabold tracking-wider"
            >
              <tr>
                <th class="p-4">Order ID</th>
                <th class="p-4">Supplier</th>
                <th class="p-4">Status</th>
                <th class="p-4">Order Date</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-slate-100">
              <tr
                v-for="(order, index) in recentOrders"
                :key="order.id ?? index"
                class="hover:bg-slate-50/60"
              >
                <td class="p-4 font-bold text-[#213A57]">
                  {{ order.po_number ?? order.order_number ?? order.id ?? '—' }}
                </td>

                <td class="p-4 text-slate-600">
                  {{
                    typeof order.supplier === 'object'
                      ? order.supplier?.supplier_name ?? order.supplier?.name ?? '—'
                      : order.supplier_name ?? order.supplier ?? '—'
                  }}
                </td>

                <td class="p-4">
                  <span
                    class="px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold"
                  >
                    {{ order.status ?? 'Pending' }}
                  </span>
                </td>

                <td class="p-4 text-slate-600">
                  {{ order.order_date ?? order.created_at ?? '—' }}
                </td>
              </tr>

              <tr v-if="recentOrders.length === 0">
                <td colspan="4" class="p-10 text-center text-slate-400 text-xs">
                  No purchase orders available.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>
