
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'

interface Stock {
  id: number
  medicine: number
  medicine_name: string
  supplier: number
  supplier_name: string
  location: string
  quantity_available: number
  last_updated: string
}

interface Medicine {
  id: number
  medicine_name: string
}

interface Supplier {
  id: number
  supplier_name: string
}

interface StockForm {
  medicine: number | ''
  supplier: number | ''
  location: string
  quantity_available: number
}

function emptyForm(): StockForm {
  return {
    medicine: '',
    supplier: '',
    location: '',
    quantity_available: 50,
  }
}

const stockList = ref<Stock[]>([])
const medicines = ref<Medicine[]>([])
const suppliers = ref<Supplier[]>([])

const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)

const loading = ref(false)
const saving = ref(false)
const deletingId = ref<number | null>(null)

const error = ref('')
const success = ref('')
const form = ref<StockForm>(emptyForm())

async function fetchStocks() {
  loading.value = true
  error.value = ''

  try {
    const response = await api.get<Stock[]>('/stocks/')
    stockList.value = Array.isArray(response.data)
      ? response.data
      : []
  } catch (err: any) {
    error.value =
      err.response?.data?.detail ||
      err.response?.data?.message ||
      'Failed to load stock records.'
  } finally {
    loading.value = false
  }
}

async function fetchMedicines() {
  try {
    const response = await api.get<Medicine[]>('/medicines/')

    medicines.value = Array.isArray(response.data)
      ? response.data
      : []
  } catch (err: any) {
    error.value =
      err.response?.data?.detail ||
      'Failed to load medicines. Check the medicines API.'
  }
}

async function fetchSuppliers() {
  try {
    const response = await api.get<Supplier[]>('/suppliers/')

    suppliers.value = Array.isArray(response.data)
      ? response.data
      : []
  } catch (err: any) {
    error.value =
      err.response?.data?.detail ||
      'Failed to load suppliers. Check the suppliers API.'
  }
}

function formatDate(value: string) {
  if (!value) return '—'

  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleString()
}

function openAddModal() {
  error.value = ''
  success.value = ''
  isEditing.value = false
  editingId.value = null
  form.value = emptyForm()
  showModal.value = true
}

function openEditModal(stock: Stock) {
  error.value = ''
  success.value = ''
  isEditing.value = true
  editingId.value = stock.id

  form.value = {
    medicine: stock.medicine,
    supplier: stock.supplier,
    location: stock.location,
    quantity_available: stock.quantity_available,
  }

  showModal.value = true
}

function closeModal() {
  if (saving.value) return
  showModal.value = false
}

async function submitForm() {
  error.value = ''
  success.value = ''

  const medicineId = Number(form.value.medicine)
  const supplierId = Number(form.value.supplier)
  const quantity = Number(form.value.quantity_available)

  if (
    form.value.medicine === '' ||
    !Number.isInteger(medicineId) ||
    medicineId <= 0
  ) {
    error.value = 'Please select a valid medicine.'
    return
  }

  if (
    form.value.supplier === '' ||
    !Number.isInteger(supplierId) ||
    supplierId <= 0
  ) {
    error.value = 'Please select a valid supplier.'
    return
  }

  if (
    !Number.isInteger(quantity) ||
    quantity < 0
  ) {
    error.value =
      'Quantity must be a whole number greater than or equal to zero.'
    return
  }

  if (!form.value.location.trim()) {
    error.value = 'Please enter a stock location.'
    return
  }

  const medicineExists = medicines.value.some(
    medicine => medicine.id === medicineId,
  )

  const supplierExists = suppliers.value.some(
    supplier => supplier.id === supplierId,
  )

  if (!medicineExists || !supplierExists) {
    error.value =
      'The selected medicine or supplier is no longer available. Refresh the list and try again.'
    return
  }

  saving.value = true

  const payload = {
    medicine: medicineId,
    supplier: supplierId,
    location: form.value.location.trim(),
    quantity_available: quantity,
  }

  console.log('Stock payload:', payload)

  try {
    if (isEditing.value && editingId.value !== null) {
      const id = editingId.value

      const response = await api.put<Stock>(
        `/stocks/${id}/`,
        payload,
      )

      const index = stockList.value.findIndex(
        stock => stock.id === id,
      )

      if (index !== -1) {
        stockList.value[index] = response.data
      } else {
        await fetchStocks()
      }

      success.value = 'Stock record updated successfully.'
    } else {
      const response = await api.post<Stock>(
        '/stocks/',
        payload,
      )

      stockList.value.push(response.data)
      success.value = 'Stock record added successfully.'
    }

    showModal.value = false
    form.value = emptyForm()
    isEditing.value = false
    editingId.value = null
  } catch (err: any) {
    const data = err.response?.data

    if (data && typeof data === 'object') {
      error.value = Object.entries(data)
        .map(([field, messages]) => {
          const detail = Array.isArray(messages)
            ? messages.join(', ')
            : typeof messages === 'object'
              ? JSON.stringify(messages)
              : String(messages)

          return `${field}: ${detail}`
        })
        .join('\n')
    } else {
      error.value =
        'Failed to save the stock record. Check your connection and try again.'
    }
  } finally {
    saving.value = false
  }
}

async function deleteStock(id: number) {
  const stock = stockList.value.find(item => item.id === id)
  if (!stock) return

  if (
    !window.confirm(
      `Are you sure you want to delete stock record #${id} (${stock.medicine_name})?`,
    )
  ) {
    return
  }

  error.value = ''
  success.value = ''
  deletingId.value = id

  try {
    await api.delete(`/stocks/${id}/`)

    stockList.value = stockList.value.filter(
      item => item.id !== id,
    )

    success.value = 'Stock record deleted successfully.'
  } catch (err: any) {
    error.value =
      err.response?.data?.message ||
      err.response?.data?.detail ||
      'Failed to delete the stock record.'
  } finally {
    deletingId.value = null
  }
}

onMounted(async () => {
  await Promise.all([
    fetchStocks(),
    fetchMedicines(),
    fetchSuppliers(),
  ])
})
</script>

<template>
  <div class="w-full min-w-0 space-y-6 overflow-y-auto pb-6 scrollbar-hide">
    <!-- Header Banner -->
    <div
      class="relative flex flex-col gap-4 overflow-hidden rounded-3xl border border-slate-200/85 bg-white p-7 shadow-sm sm:flex-row sm:items-center sm:justify-between"
    >
      <div
        class="pointer-events-none absolute right-0 top-0 h-32 w-32 rounded-bl-full bg-gradient-to-br from-[#0AD1C8]/10 to-[#80ED99]/20"
      ></div>

      <div class="relative z-10 space-y-1">
        <h1 class="text-2xl font-extrabold tracking-tight text-[#213A57]">
          Stock &amp; Location Inventory
        </h1>
        <p class="text-xs font-medium text-slate-500">
          Track storage locations, quantities available, and supplier associations.
        </p>
      </div>

      <button
        @click="openAddModal"
        class="relative z-10 flex items-center space-x-2.5 rounded-2xl bg-gradient-to-r from-[#0B6477] to-[#14919B] px-5 py-3 text-xs font-bold text-white shadow-lg shadow-[#14919B]/20 transition-all hover:-translate-y-0.5 hover:opacity-95"
      >
        <i class="fa-solid fa-boxes-stacked text-sm"></i>
        <span>Add Stock</span>
      </button>
    </div>

    <!-- Success Message -->
    <div
      v-if="success"
      class="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700"
    >
      {{ success }}
    </div>

    <!-- Error Message -->
    <div
      v-if="error"
      class="whitespace-pre-line rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-600"
    >
      {{ error }}
    </div>

    <!-- Stock Table -->
    <div class="min-w-0 space-y-4 rounded-3xl border border-slate-200/80 bg-white p-6 shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead
            class="border-b border-slate-100 bg-slate-50/80 text-[10px] font-extrabold uppercase tracking-wider text-slate-500"
          >
            <tr>
              <th class="p-4">ID</th>
              <th class="p-4">Medicine</th>
              <th class="p-4">Supplier</th>
              <th class="p-4">Location / Shelf</th>
              <th class="p-4">Quantity Available</th>
              <th class="p-4">Last Updated</th>
              <th class="p-4 text-right">Actions</th>
            </tr>
          </thead>

          <tbody class="divide-y divide-slate-100">
            <tr v-if="loading">
              <td colspan="7" class="p-8 text-center text-sm text-slate-500">
                <i class="fa-solid fa-spinner fa-spin mr-2"></i>
                Loading stock records...
              </td>
            </tr>

            <tr v-else-if="stockList.length === 0">
              <td colspan="7" class="p-8 text-center text-sm text-slate-500">
                No stock records found. Add your first stock record.
              </td>
            </tr>

            <tr
              v-for="stk in stockList"
              v-else
              :key="stk.id"
              class="transition-colors hover:bg-slate-50/60"
            >
              <td class="p-4 font-mono font-bold text-slate-500">
                #{{ stk.id }}
              </td>
              <td class="p-4 font-bold text-slate-900">
                {{ stk.medicine_name }}
              </td>
              <td class="p-4 text-xs text-slate-600">
                {{ stk.supplier_name }}
              </td>
              <td class="p-4 text-xs font-semibold text-slate-700">
                {{ stk.location }}
              </td>
              <td class="p-4 font-extrabold text-[#0B6477]">
                {{ stk.quantity_available }} units
              </td>
              <td class="p-4 font-mono text-xs text-slate-600">
                {{ formatDate(stk.last_updated) }}
              </td>
              <td class="p-4">
                <div class="flex justify-end gap-2">
                  <button
                    @click="openEditModal(stk)"
                    class="rounded-xl bg-sky-50 px-3 py-1.5 text-xs font-semibold text-sky-700 transition hover:bg-sky-100"
                  >
                    <i class="fa-solid fa-pen-to-square mr-1"></i>
                    Edit
                  </button>

                  <button
                    @click="deleteStock(stk.id)"
                    :disabled="deletingId === stk.id"
                    class="rounded-xl bg-rose-50 px-3 py-1.5 text-xs font-semibold text-rose-600 transition hover:bg-rose-100 disabled:opacity-50"
                  >
                    <i
                      v-if="deletingId === stk.id"
                      class="fa-solid fa-spinner fa-spin mr-1"
                    ></i>
                    {{ deletingId === stk.id ? 'Deleting...' : 'Delete' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Refresh -->
      <div class="flex justify-end border-t border-slate-100 pt-4">
        <button
          @click="fetchStocks"
          :disabled="loading"
          class="rounded-xl bg-slate-100 px-4 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-200 disabled:opacity-50"
        >
          <i class="fa-solid fa-rotate-right mr-1"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Add/Edit Stock Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-900/50 p-4 backdrop-blur-sm"
      @click.self="closeModal"
    >
      <div
        class="my-auto w-full max-w-md space-y-4 rounded-3xl border border-slate-100 bg-white p-6 shadow-xl"
      >
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 class="text-lg font-bold text-[#213A57]">
            {{ isEditing ? 'Edit Stock Record' : 'Add Stock Record' }}
          </h3>

          <button
            type="button"
            @click="closeModal"
            :disabled="saving"
            class="text-slate-400 transition hover:text-slate-600 disabled:opacity-50"
            aria-label="Close modal"
          >
            <i class="fa-solid fa-xmark text-lg"></i>
          </button>
        </div>

        <form @submit.prevent="submitForm" class="space-y-4">
          <!-- Medicine Dropdown -->
          <div>
            <label class="mb-1 block text-xs font-bold text-slate-600">
              Medicine
            </label>

            <select
              v-model="form.medicine"
              required
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs outline-none focus:border-[#14919B] focus:ring-2 focus:ring-[#14919B]/10"
            >
              <option value="" disabled>Select a medicine</option>
              <option
                v-for="medicine in medicines"
                :key="medicine.id"
                :value="medicine.id"
              >
                {{ medicine.medicine_name }}
              </option>
            </select>

            <p v-if="medicines.length === 0" class="mt-1 text-xs text-rose-500">
              No medicines available. Add a medicine first.
            </p>
          </div>

          <!-- Supplier Dropdown -->
          <select
            v-model="form.supplier"
            required
            class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs"
          >
            <option value="" disabled>Select a supplier</option>

            <option
              v-for="supplier in suppliers"
              :key="supplier.id"
              :value="supplier.id"
            >
              {{ supplier.supplier_name }}
            </option>
        </select> 
          <!-- Location -->
          <div>
            <label class="mb-1 block text-xs font-bold text-slate-600">
              Location / Shelf
            </label>
            <input
              v-model.trim="form.location"
              required
              type="text"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs outline-none focus:border-[#14919B] focus:ring-2 focus:ring-[#14919B]/10"
              placeholder="e.g. Shelf A-1"
            />
          </div>

          <!-- Quantity -->
          <div>
            <label class="mb-1 block text-xs font-bold text-slate-600">
              Quantity Available
            </label>
            <input
              v-model.number="form.quantity_available"
              required
              type="number"
              min="0"
              step="1"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs outline-none focus:border-[#14919B] focus:ring-2 focus:ring-[#14919B]/10"
              placeholder="50"
            />
          </div>

          <div class="flex justify-end space-x-3 border-t border-slate-100 pt-3">
            <button
              type="button"
              @click="closeModal"
              :disabled="saving"
              class="rounded-xl bg-slate-100 px-4 py-2 text-xs text-slate-600 transition hover:bg-slate-200 disabled:opacity-50"
            >
              Cancel
            </button>

            <button
              type="submit"
              :disabled="saving || medicines.length === 0 || suppliers.length === 0"
              class="rounded-xl bg-gradient-to-r from-[#0B6477] to-[#14919B] px-4 py-2 text-xs font-bold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <i v-if="saving" class="fa-solid fa-spinner fa-spin mr-1"></i>
              {{
                saving
                  ? (isEditing ? 'Updating...' : 'Saving...')
                  : (isEditing ? 'Update Stock' : 'Save Stock')
              }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
