
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

interface Supplier {
  id: number
  supplier_name: string
  supplier_address: string
  email: string
  contact_number: string
}

interface SupplierForm {
  supplier_name: string
  supplier_address: string
  email: string
  contact_number: string
}

function emptyForm(): SupplierForm {
  return {
    supplier_name: '',
    supplier_address: '',
    email: '',
    contact_number: '',
  }
}

const suppliers = ref<Supplier[]>([])
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const loading = ref(false)
const saving = ref(false)
const deletingId = ref<number | null>(null)
const error = ref('')
const success = ref('')

const form = ref<SupplierForm>(emptyForm())

// GET: Fetch all suppliers
async function fetchSuppliers() {
  loading.value = true
  error.value = ''

  try {
    const response = await api.get<Supplier[]>('/suppliers/')

    // Supports both regular arrays and paginated Django REST responses.
    const data = response.data as unknown as
      | Supplier[]
      | { results: Supplier[] }

    suppliers.value = Array.isArray(data) ? data : data.results
  } catch (err: any) {
    error.value =
      err.response?.data?.detail ||
      err.response?.data?.message ||
      'Failed to load suppliers. Check your backend connection and API URL.'
  } finally {
    loading.value = false
  }
}

// Open modal for adding a supplier
function openAddModal() {
  error.value = ''
  success.value = ''
  isEditing.value = false
  editingId.value = null
  form.value = emptyForm()
  showModal.value = true
}

// Open modal for editing a supplier
function openEditModal(supplier: Supplier) {
  error.value = ''
  success.value = ''
  isEditing.value = true
  editingId.value = supplier.id

  form.value = {
    supplier_name: supplier.supplier_name,
    supplier_address: supplier.supplier_address,
    email: supplier.email,
    contact_number: supplier.contact_number,
  }

  showModal.value = true
}

function closeModal() {
  if (saving.value) return
  showModal.value = false
}

// POST: Add a supplier; PUT: Update a supplier
async function submitForm() {
  if (saving.value) return

  saving.value = true
  error.value = ''
  success.value = ''

  try {
    if (isEditing.value && editingId.value !== null) {
      const id = editingId.value

      const response = await api.put<Supplier>(
        `/suppliers/${id}/`,
        form.value,
      )

      const index = suppliers.value.findIndex(
        supplier => supplier.id === id,
      )

      if (index !== -1) {
        suppliers.value[index] = response.data
      }

      success.value = 'Supplier updated successfully.'
    } else {
      const response = await api.post<Supplier>(
        '/suppliers/',
        form.value,
      )

      suppliers.value.push(response.data)
      success.value = 'Supplier registered successfully.'
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
            : String(messages)

          return `${field}: ${detail}`
        })
        .join('\n')
    } else {
      error.value =
        'The supplier could not be saved. Check your connection and try again.'
    }
  } finally {
    saving.value = false
  }
}

// DELETE: ADMIN only
async function deleteSupplier(id: number) {
  if (!auth.isAdmin || deletingId.value !== null) return

  const supplier = suppliers.value.find(
    item => item.id === id,
  )

  if (!supplier) return

  if (
    !window.confirm(
      `Are you sure you want to delete "${supplier.supplier_name}"?`,
    )
  ) {
    return
  }

  deletingId.value = id
  error.value = ''
  success.value = ''

  try {
    await api.delete(`/suppliers/${id}/`)

    suppliers.value = suppliers.value.filter(
      item => item.id !== id,
    )

    success.value = 'Supplier deleted successfully.'
  } catch (err: any) {
    error.value =
      err.response?.data?.message ||
      err.response?.data?.detail ||
      'Failed to delete supplier. It may be referenced by another record.'
  } finally {
    deletingId.value = null
  }
}

onMounted(fetchSuppliers)
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
          Supplier Directory
        </h1>
        <p class="text-xs font-medium text-slate-500">
          Manage pharmaceutical suppliers, addresses, emails, and contact numbers.
        </p>
      </div>

      <button
        @click="openAddModal"
        class="relative z-10 flex items-center space-x-2.5 rounded-2xl bg-gradient-to-r from-[#0B6477] to-[#14919B] px-5 py-3 text-xs font-bold text-white shadow-lg shadow-[#14919B]/20 transition-all hover:-translate-y-0.5 hover:opacity-95"
      >
        <i class="fa-solid fa-truck text-sm"></i>
        <span>Register Supplier</span>
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

    <!-- Supplier Records Card -->
    <div
      class="w-full min-w-0 space-y-4 rounded-3xl border border-slate-200/80 bg-white p-6 shadow-sm"
    >
      <!-- Records Header and Refresh Button -->
      <div
        class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <h2 class="text-lg font-extrabold text-[#213A57]">
            Supplier Records
          </h2>
          <p class="mt-1 text-xs text-slate-500">
            View and manage registered suppliers.
          </p>
        </div>

        <button
          @click="fetchSuppliers"
          :disabled="loading"
          class="inline-flex items-center justify-center gap-2 self-start rounded-xl border border-[#14919B]/30 bg-[#14919B]/10 px-4 py-2.5 text-xs font-bold text-[#0B6477] shadow-sm transition-all hover:border-[#14919B]/50 hover:bg-[#14919B]/20 disabled:cursor-not-allowed disabled:opacity-50 sm:self-auto"
        >
          <i
            class="fa-solid fa-rotate-right"
            :class="{ 'animate-spin': loading }"
          ></i>
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
      </div>

      <!-- Supplier Table -->
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead
            class="border-b border-slate-100 bg-slate-50/80 text-[10px] font-extrabold uppercase tracking-wider text-slate-500"
          >
            <tr>
              <th class="p-4">ID</th>
              <th class="p-4">Supplier Name</th>
              <th class="p-4">Address</th>
              <th class="p-4">Email</th>
              <th class="p-4">Contact Number</th>
              <th class="p-4 text-right">Actions</th>
            </tr>
          </thead>

          <tbody class="divide-y divide-slate-100">
            <tr v-if="loading">
              <td colspan="6" class="p-8 text-center text-sm text-slate-500">
                <i class="fa-solid fa-spinner fa-spin mr-2"></i>
                Loading suppliers...
              </td>
            </tr>

            <tr v-else-if="suppliers.length === 0">
              <td colspan="6" class="p-8 text-center text-sm text-slate-500">
                No suppliers found. Register your first supplier.
              </td>
            </tr>

            <tr
              v-for="sup in suppliers"
              :key="sup.id"
              class="transition-colors hover:bg-slate-50/60"
            >
              <td class="p-4 font-mono font-bold text-slate-500">
                #{{ sup.id }}
              </td>

              <td class="p-4 font-bold text-slate-900">
                {{ sup.supplier_name }}
              </td>

              <td class="p-4 text-xs text-slate-600">
                {{ sup.supplier_address }}
              </td>

              <td class="p-4 font-mono text-xs text-slate-600">
                {{ sup.email }}
              </td>

              <td class="p-4 font-mono text-xs text-slate-600">
                {{ sup.contact_number }}
              </td>

              <td class="p-4">
                <div class="flex justify-end gap-2">
                  <!-- ADMIN and STAFF can edit -->
                  <button
                    @click="openEditModal(sup)"
                    class="rounded-xl bg-sky-50 px-3 py-1.5 text-xs font-semibold text-sky-700 transition hover:bg-sky-100"
                  >
                    <i class="fa-solid fa-pen-to-square mr-1"></i>
                    Edit
                  </button>

                  <!-- ADMIN only can delete -->
                  <button
                    v-if="auth.isAdmin"
                    @click="deleteSupplier(sup.id)"
                    :disabled="deletingId === sup.id"
                    class="rounded-xl bg-rose-50 px-3 py-1.5 text-xs font-semibold text-rose-600 transition hover:bg-rose-100 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <i
                      v-if="deletingId === sup.id"
                      class="fa-solid fa-spinner fa-spin mr-1"
                    ></i>
                    {{ deletingId === sup.id ? 'Deleting...' : 'Delete' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add/Edit Supplier Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-900/50 p-4 backdrop-blur-sm"
      @click.self="closeModal"
    >
      <div
        class="my-auto w-full max-w-md space-y-4 rounded-3xl border border-slate-100 bg-white p-6 shadow-xl"
      >
        <div
          class="flex items-center justify-between border-b border-slate-100 pb-3"
        >
          <h3 class="text-lg font-bold text-[#213A57]">
            {{ isEditing ? 'Edit Supplier' : 'Register Supplier' }}
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
          <div>
            <label class="mb-1 block text-xs font-bold text-slate-600">
              Supplier Name
            </label>
            <input
              v-model.trim="form.supplier_name"
              required
              type="text"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs outline-none transition focus:border-[#14919B] focus:ring-2 focus:ring-[#14919B]/10"
              placeholder="e.g. PharmaCore Distribution"
            />
          </div>

          <div>
            <label class="mb-1 block text-xs font-bold text-slate-600">
              Supplier Address
            </label>
            <input
              v-model.trim="form.supplier_address"
              required
              type="text"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs outline-none transition focus:border-[#14919B] focus:ring-2 focus:ring-[#14919B]/10"
              placeholder="Tuguegarao City, Cagayan"
            />
          </div>

          <div>
            <label class="mb-1 block text-xs font-bold text-slate-600">
              Email Address
            </label>
            <input
              v-model.trim="form.email"
              required
              type="email"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs outline-none transition focus:border-[#14919B] focus:ring-2 focus:ring-[#14919B]/10"
              placeholder="contact@pharmacore.com"
            />
          </div>

          <div>
            <label class="mb-1 block text-xs font-bold text-slate-600">
              Contact Number
            </label>
            <input
              v-model.trim="form.contact_number"
              required
              type="text"
              maxlength="30"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs outline-none transition focus:border-[#14919B] focus:ring-2 focus:ring-[#14919B]/10"
              placeholder="+63 917 123 4567"
            />
          </div>

          <div
            class="flex justify-end space-x-3 border-t border-slate-100 pt-3"
          >
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
              :disabled="saving"
              class="rounded-xl bg-gradient-to-r from-[#0B6477] to-[#14919B] px-4 py-2 text-xs font-bold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <i v-if="saving" class="fa-solid fa-spinner fa-spin mr-1"></i>
              {{
                saving
                  ? (isEditing ? 'Updating...' : 'Saving...')
                  : (isEditing ? 'Update Supplier' : 'Save Supplier')
              }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
