
<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import axios from 'axios'
import api from '@/services/api'

interface Medicine {
  id: number
  medicine_name: string
  brand_name: string
  category: string
  dosage_form: string
  strength: string
  reorder_level: number
  medicine_type: string
  manufacturer: string
  expiry_date: string
}

interface MedicineForm {
  medicine_name: string
  brand_name: string
  category: string
  dosage_form: string
  strength: string
  reorder_level: number
  medicine_type: string
  manufacturer: string
  expiry_date: string
}

const medicines = ref<Medicine[]>([])
const loading = ref(false)
const saving = ref(false)
const deletingId = ref<number | null>(null)
const showModal = ref(false)
const error = ref('')
const success = ref('')

function createEmptyForm(): MedicineForm {
  return {
    medicine_name: '',
    brand_name: '',
    category: '',
    dosage_form: '',
    strength: '',
    reorder_level: 30,
    medicine_type: '',
    manufacturer: '',
    expiry_date: '',
  }
}

const form = reactive<MedicineForm>(createEmptyForm())

function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data

    if (typeof data === 'string') {
      return data
    }

    if (data && typeof data === 'object') {
      return Object.entries(data)
        .map(([field, messages]) => {
          const detail = Array.isArray(messages)
            ? messages.join(', ')
            : typeof messages === 'string'
              ? messages
              : JSON.stringify(messages)

          return `${field}: ${detail}`
        })
        .join(' | ')
    }

    if (err.response) {
      return `Request failed with status ${err.response.status}.`
    }

    return 'Cannot connect to Django. Check that the backend server is running.'
  }

  return 'An unexpected error occurred.'
}

async function fetchMedicines() {
  loading.value = true
  error.value = ''

  try {
    const response = await api.get('/medicines/')
    const data = response.data

    if (Array.isArray(data)) {
      medicines.value = data
    } else if (Array.isArray(data?.results)) {
      medicines.value = data.results
    } else {
      medicines.value = []
      error.value = 'Unexpected response format from Django.'
    }

    console.log('Medicines returned by Django:', medicines.value)
    console.log('Total medicines:', medicines.value.length)
  } catch (err: unknown) {
    error.value = `Failed to load medicines. ${getErrorMessage(err)}`
    console.error('Fetch medicines error:', err)
  } finally {
    loading.value = false
  }
}

function openModal() {
  error.value = ''
  success.value = ''
  Object.assign(form, createEmptyForm())
  showModal.value = true
}

function closeModal() {
  if (saving.value) return
  showModal.value = false
}

async function submitForm() {
  saving.value = true
  error.value = ''
  success.value = ''

  try {
    await api.post('/medicines/', { ...form })

    showModal.value = false
    Object.assign(form, createEmptyForm())

    success.value = 'Medicine added successfully.'
    await fetchMedicines()
  } catch (err: unknown) {
    error.value = `Failed to add medicine. ${getErrorMessage(err)}`
    console.error('Add medicine error:', err)
  } finally {
    saving.value = false
  }
}

async function deleteMedicine(id: number) {
  if (deletingId.value !== null) return

  const confirmed = window.confirm(
    'Are you sure you want to delete this medicine?'
  )

  if (!confirmed) return

  deletingId.value = id
  error.value = ''
  success.value = ''

  try {
    await api.delete(`/medicines/${id}/`)

    medicines.value = medicines.value.filter(
      (medicine) => medicine.id !== id
    )

    success.value = 'Medicine deleted successfully.'
  } catch (err: unknown) {
    error.value = `Failed to delete medicine. ${getErrorMessage(err)}`
    console.error('Delete medicine error:', err)
  } finally {
    deletingId.value = null
  }
}

onMounted(() => {
  fetchMedicines()
})
</script>

<template>
  <div class="space-y-6 overflow-y-auto w-full pb-6">
    <!-- Header -->
    <div
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-7 rounded-3xl border border-slate-200/85 shadow-sm relative overflow-hidden"
    >
      <div
        class="absolute right-0 top-0 w-32 h-32 bg-gradient-to-br from-[#0AD1C8]/10 to-[#80ED99]/20 rounded-bl-full pointer-events-none"
      ></div>

      <div class="space-y-1 relative z-10">
        <h1 class="text-2xl font-extrabold text-[#213A57] tracking-tight">
          Medicine Directory
        </h1>
        <p class="text-xs text-slate-500 font-medium">
          Manage pharmaceutical items, brand names, dosages, and expiry dates.
        </p>
      </div>

      <button
        @click="openModal"
        class="bg-gradient-to-r from-[#0B6477] to-[#14919B] hover:opacity-95 text-white px-5 py-3 rounded-2xl text-xs font-bold shadow-lg shadow-[#14919B]/20 transition-all flex items-center space-x-2.5 relative z-10"
      >
        <i class="fa-solid fa-plus text-sm"></i>
        <span>Add New Medicine</span>
      </button>
    </div>

    <!-- Success Message -->
    <div
      v-if="success"
      class="p-4 rounded-xl bg-emerald-50 text-emerald-700 text-sm border border-emerald-200"
      role="status"
    >
      {{ success }}
    </div>

    <!-- Error Message -->
    <div
      v-if="error"
      class="p-4 rounded-xl bg-rose-50 text-rose-700 text-sm border border-rose-200"
      role="alert"
    >
      {{ error }}
    </div>

    <!-- Medicine Table -->
    <div
      class="bg-white border border-slate-200/80 rounded-3xl p-6 shadow-sm space-y-4"
    >
      <div class="flex items-center justify-between">
        <div>
          <h2 class="font-bold text-[#213A57]">Medicine Records</h2>
          <p class="text-xs text-slate-500 mt-1">
            Total records: {{ medicines.length }}
          </p>
        </div>

        <button
          @click="fetchMedicines"
          :disabled="loading"
          class="text-xs font-semibold text-[#0B6477] hover:underline disabled:opacity-50"
        >
          <i class="fa-solid fa-rotate-right mr-1"></i>
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead
            class="bg-slate-50/80 text-slate-500 uppercase text-[10px] font-extrabold tracking-wider border-b border-slate-100"
          >
            <tr>
              <th class="p-4">ID</th>
              <th class="p-4">Medicine Name</th>
              <th class="p-4">Brand</th>
              <th class="p-4">Category</th>
              <th class="p-4">Dosage / Strength</th>
              <th class="p-4">Manufacturer</th>
              <th class="p-4">Expiry</th>
              <th class="p-4 text-right">Actions</th>
            </tr>
          </thead>

          <tbody class="divide-y divide-slate-100">
            <tr v-if="loading && medicines.length === 0">
              <td colspan="8" class="p-8 text-center text-slate-500">
                Loading medicines...
              </td>
            </tr>

            <tr v-else-if="!loading && medicines.length === 0">
              <td colspan="8" class="p-8 text-center text-slate-500">
                No medicine records found.
              </td>
            </tr>

            <tr
              v-for="med in medicines"
              :key="med.id"
              class="hover:bg-slate-50/60 transition-colors"
            >
              <td class="p-4 font-mono font-bold text-slate-500">
                #{{ med.id }}
              </td>

              <td class="p-4 font-bold text-slate-900">
                {{ med.medicine_name }}
              </td>

              <td class="p-4 text-slate-600 text-xs">
                {{ med.brand_name }}
              </td>

              <td class="p-4">
                <span
                  class="px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold"
                >
                  {{ med.category }}
                </span>
              </td>

              <td class="p-4 text-slate-600 text-xs">
                {{ med.dosage_form }} ({{ med.strength }})
              </td>

              <td class="p-4 text-slate-600 text-xs">
                {{ med.manufacturer }}
              </td>

              <td class="p-4 text-slate-600 text-xs font-mono">
                {{ med.expiry_date }}
              </td>

              <td class="p-4 text-right">
                <button
                  @click="deleteMedicine(med.id)"
                  :disabled="deletingId === med.id"
                  class="bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all disabled:opacity-50"
                >
                  {{ deletingId === med.id ? 'Deleting...' : 'Delete' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Medicine Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 p-4 overflow-y-auto"
      @click.self="closeModal"
    >
      <div
        class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-xl space-y-4 border border-slate-100 my-auto"
      >
        <div class="flex justify-between items-center border-b border-slate-100 pb-3">
          <h3 class="text-lg font-bold text-[#213A57]">
            Add New Medicine
          </h3>

          <button
            type="button"
            @click="closeModal"
            :disabled="saving"
            class="text-slate-400 hover:text-slate-600"
            aria-label="Close modal"
          >
            <i class="fa-solid fa-xmark text-lg"></i>
          </button>
        </div>

        <form
          @submit.prevent="submitForm"
          class="grid grid-cols-1 sm:grid-cols-2 gap-4"
        >
          <div>
            <label class="block text-xs font-bold text-slate-600 mb-1">
              Medicine Name
            </label>
            <input
              v-model.trim="form.medicine_name"
              required
              type="text"
              class="medicine-input"
              placeholder="e.g. Paracetamol"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-600 mb-1">
              Brand Name
            </label>
            <input
              v-model.trim="form.brand_name"
              required
              type="text"
              class="medicine-input"
              placeholder="e.g. Biogesic"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-600 mb-1">
              Category
            </label>
            <input
              v-model.trim="form.category"
              required
              type="text"
              class="medicine-input"
              placeholder="e.g. Analgesic"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-600 mb-1">
              Dosage Form
            </label>
            <input
              v-model.trim="form.dosage_form"
              required
              type="text"
              class="medicine-input"
              placeholder="e.g. Tablet"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-600 mb-1">
              Strength
            </label>
            <input
              v-model.trim="form.strength"
              required
              type="text"
              class="medicine-input"
              placeholder="e.g. 500mg"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-600 mb-1">
              Reorder Level
            </label>
            <input
              v-model.number="form.reorder_level"
              required
              min="0"
              type="number"
              class="medicine-input"
              placeholder="30"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-600 mb-1">
              Medicine Type
            </label>
            <input
              v-model.trim="form.medicine_type"
              required
              type="text"
              class="medicine-input"
              placeholder="e.g. Branded"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-600 mb-1">
              Manufacturer
            </label>
            <input
              v-model.trim="form.manufacturer"
              required
              type="text"
              class="medicine-input"
              placeholder="e.g. Unilab"
            />
          </div>

          <div class="sm:col-span-2">
            <label class="block text-xs font-bold text-slate-600 mb-1">
              Expiry Date
            </label>
            <input
              v-model="form.expiry_date"
              required
              type="date"
              class="medicine-input"
            />
          </div>

          <div class="sm:col-span-2 flex justify-end space-x-3 pt-3 border-t border-slate-100">
            <button
              type="button"
              @click="closeModal"
              :disabled="saving"
              class="px-4 py-2 rounded-xl text-xs bg-slate-100 text-slate-600 disabled:opacity-50"
            >
              Cancel
            </button>

            <button
              type="submit"
              :disabled="saving"
              class="px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-[#0B6477] to-[#14919B] text-white disabled:opacity-50"
            >
              {{ saving ? 'Saving...' : 'Save Medicine' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.medicine-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  font-size: 0.75rem;
  background: #f8fafc;
  outline: none;
}

.medicine-input:focus {
  border-color: #14919b;
  box-shadow: 0 0 0 2px rgb(20 145 155 / 15%);
}
</style>
