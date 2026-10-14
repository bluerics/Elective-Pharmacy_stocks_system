<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

interface Supplier {
  id: number
  supplier_name: string
}

interface Medicine {
  id: number
  medicine_name: string
  strength?: string
}

interface PurchaseOrder {
  id: number
  supplier: number
  supplier_name?: string
  order_date: string
  total_amount: number | string
  status: string
  stock_received: boolean
}

interface PurchaseOrderDetail {
  id: number
  order: number
  medicine: number
  quantity_order: number
  unit_cost: number | string
  subtotal: number | string
}

interface OrderForm {
  supplier: number
  medicine: number
  quantity_order: number
  unit_cost: number
  status: string
}

const purchaseOrders = ref<PurchaseOrder[]>([])
const orderDetails = ref<PurchaseOrderDetail[]>([])
const suppliers = ref<Supplier[]>([])
const medicines = ref<Medicine[]>([])

const loading = ref(false)
const saving = ref(false)
const deletingId = ref<number | null>(null)
const receivingId = ref<number | null>(null)
const detailsLoadingId = ref<number | null>(null)

const showModal = ref(false)
const showSuggestions = ref(false)
const expandedOrderId = ref<number | null>(null)

const error = ref('')
const success = ref('')
const medicineInput = ref('')

function emptyForm(): OrderForm {
  return {
    supplier: 0,
    medicine: 0,
    quantity_order: 100,
    unit_cost: 50,
    status: 'PENDING',
  }
}

const form = ref<OrderForm>(emptyForm())

const filteredMedicines = computed(() => {
  const query = medicineInput.value.trim().toLowerCase()

  if (!query) return []

  return medicines.value.filter(medicine =>
    medicine.medicine_name.toLowerCase().includes(query),
  )
})

const estimatedTotal = computed(() => {
  const quantity = Number(form.value.quantity_order)
  const cost = Number(form.value.unit_cost)

  if (
    !Number.isFinite(quantity) ||
    !Number.isFinite(cost)
  ) {
    return 0
  }

  return quantity * cost
})

// Validate the selected values directly.
const canSubmit = computed(() => {
  const supplierId = Number(form.value.supplier)
  const medicineId = Number(form.value.medicine)
  const quantity = Number(form.value.quantity_order)
  const unitCost = Number(form.value.unit_cost)

  return (
    !saving.value &&
    Number.isInteger(supplierId) &&
    supplierId > 0 &&
    Number.isInteger(medicineId) &&
    medicineId > 0 &&
    Number.isInteger(quantity) &&
    quantity > 0 &&
    Number.isFinite(unitCost) &&
    unitCost >= 0
  )
})

function supplierName(id: number) {
  return suppliers.value.find(
    supplier => supplier.id === id,
  )?.supplier_name ?? `Supplier #${id}`
}

function medicineName(id: number) {
  return medicines.value.find(
    medicine => medicine.id === id,
  )?.medicine_name ?? `Medicine #${id}`
}

function formatCurrency(value: number | string) {
  const amount = Number(value)

  return `₱${Number.isFinite(amount)
    ? amount.toLocaleString('en-PH', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })
    : '0.00'}`
}

function formatDate(value?: string) {
  if (!value) return '—'

  const date = new Date(`${value}T00:00:00`)

  if (Number.isNaN(date.getTime())) return value

  return date.toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function displayStatus(status: string) {
  const labels: Record<string, string> = {
    PENDING: 'Pending',
    APPROVED: 'Approved',
    RECEIVED: 'Received',
    CANCELLED: 'Cancelled',
  }

  return labels[status] ?? status
}

function statusClass(status: string) {
  const classes: Record<string, string> = {
    PENDING: 'border-amber-200 bg-amber-50 text-amber-700',
    APPROVED: 'border-sky-200 bg-sky-50 text-sky-700',
    RECEIVED: 'border-emerald-200 bg-emerald-50 text-emerald-700',
    CANCELLED: 'border-rose-200 bg-rose-50 text-rose-700',
  }

  return classes[status] ??
    'border-slate-200 bg-slate-50 text-slate-700'
}

function detailsForOrder(orderId: number) {
  return orderDetails.value.filter(
    detail => Number(detail.order) === Number(orderId),
  )
}

async function fetchOrders() {
  loading.value = true
  error.value = ''

  try {
    const response = await api.get<PurchaseOrder[]>(
      '/purchase_orders/',
    )

    purchaseOrders.value = response.data
  } catch (err: any) {
    error.value =
      err.response?.data?.detail ||
      'Failed to load purchase orders. Check your backend and API URL.'
  } finally {
    loading.value = false
  }
}

async function fetchOrderDetails() {
  try {
    const response = await api.get<PurchaseOrderDetail[]>(
      '/purchase_order_details/',
    )

    orderDetails.value = response.data
  } catch {
    error.value = 'Failed to load purchase-order details.'
  }
}

async function fetchSuppliers() {
  try {
    const response = await api.get<Supplier[]>('/suppliers/')

    suppliers.value = response.data
  } catch {
    error.value = 'Failed to load suppliers.'
  }
}

async function fetchMedicines() {
  try {
    const response = await api.get<Medicine[]>('/medicines/')

    medicines.value = response.data
  } catch {
    error.value = 'Failed to load medicines.'
  }
}

async function refreshAll() {
  await Promise.all([
    fetchOrders(),
    fetchOrderDetails(),
  ])
}

function openModal() {
  error.value = ''
  success.value = ''
  form.value = emptyForm()
  medicineInput.value = ''
  showSuggestions.value = false
  showModal.value = true
}

function closeModal() {
  if (saving.value) return

  showModal.value = false
  showSuggestions.value = false
}

function onMedicineInput() {
  // A changed name invalidates the previous medicine selection.
  form.value.medicine= 0
  showSuggestions.value = true
}

function selectMedicine(medicine: Medicine) {
  form.value.medicine= Number(medicine.id)
  medicineInput.value = medicine.medicine_name
  showSuggestions.value = false
}

async function submitForm() {
  if (saving.value) return

  error.value = ''
  success.value = ''

  const supplierId = Number(form.value.supplier)
  const medicineId = Number(form.value.medicine)
  const quantity = Number(form.value.quantity_order)
  const unitCost = Number(form.value.unit_cost)

  // Revalidate inside the handler, even if the button is enabled.
  if (
    !Number.isInteger(supplierId) ||
    supplierId <= 0 ||
    !suppliers.value.some(
      supplier => Number(supplier.id) === supplierId,
    )
  ) {
    error.value = 'Please select a valid supplier.'
    return
  }

  if (
    !Number.isInteger(medicineId) ||
    medicineId <= 0 ||
    !medicines.value.some(
      medicine => Number(medicine.id) === medicineId,
    )
  ) {
    error.value = 'Please select a valid medicine from the suggestions.'
    return
  }

  if (!Number.isInteger(quantity) || quantity <= 0) {
    error.value = 'Quantity must be a positive whole number.'
    return
  }

  if (!Number.isFinite(unitCost) || unitCost < 0) {
    error.value = 'Unit cost must be a valid non-negative amount.'
    return
  }

  saving.value = true

  let createdOrderId: number | null = null

  try {
    const total = quantity * unitCost

    // Create the purchase-order header.
    const orderResponse = await api.post<PurchaseOrder>(
      '/purchase_orders/',
      {
        supplier: supplierId,
        total_amount: total.toFixed(2),
        status: form.value.status,
      },
    )

    createdOrderId = Number(orderResponse.data.id)

    if (!Number.isInteger(createdOrderId) || createdOrderId <= 0) {
      throw new Error(
        'The server did not return a valid purchase-order ID.',
      )
    }

    // Create the associated medicine detail.
    try {
      await api.post<PurchaseOrderDetail>(
        '/purchase_order_details/',
        {
          order: createdOrderId,
          medicine: medicineId,
          quantity_order: quantity,
          unit_cost: unitCost.toFixed(2),
        },
      )
    } catch (detailError) {
      // Attempt cleanup if creating the detail fails.
      try {
        await api.delete(
          `/purchase_orders/${createdOrderId}/`,
        )
      } catch {
        throw new Error(
          'The purchase order was created, but its medicine detail failed and cleanup also failed. Check the order before retrying.',
        )
      }

      throw detailError
    }

    // Reload data. A refresh failure should not undo a successful creation.
    showModal.value = false
    form.value = emptyForm()
    medicineInput.value = ''
    showSuggestions.value = false

    success.value =
      `Purchase order #${createdOrderId} created successfully.`

    try {
      await refreshAll()
    } catch {
      // The order was already created successfully.
    }
  } catch (err: any) {
    const data = err.response?.data

    if (data && typeof data === 'object') {
      error.value = Object.entries(data)
        .map(([field, messages]) => {
          const message = Array.isArray(messages)
            ? messages.join(', ')
            : String(messages)

          return `${field}: ${message}`
        })
        .join('\n')
    } else {
      error.value =
        err.message ||
        'Failed to create the purchase order. Check your API endpoints and backend connection.'
    }
  } finally {
    saving.value = false
  }
}

async function toggleDetails(orderId: number) {
  if (expandedOrderId.value === orderId) {
    expandedOrderId.value = null
    return
  }

  expandedOrderId.value = orderId
  detailsLoadingId.value = orderId

  try {
    const response = await api.get<PurchaseOrderDetail[]>(
      '/purchase_order_details/',
    )

    orderDetails.value = response.data
  } catch {
    error.value = 'Could not load purchase-order details.'
  } finally {
    detailsLoadingId.value = null
  }
}

async function receiveOrder(order: PurchaseOrder) {
  if (order.stock_received) {
    error.value = 'This purchase order has already been received.'
    return
  }

  if (detailsForOrder(order.id).length === 0) {
    await fetchOrderDetails()
  }

  if (detailsForOrder(order.id).length === 0) {
    error.value =
      'This purchase order has no details. Add order details before receiving it.'
    return
  }

  if (
    !window.confirm(
      `Receive PO-${order.id} and update stock quantities?`,
    )
  ) {
    return
  }

  error.value = ''
  success.value = ''
  receivingId.value = order.id

  try {
    const response = await api.post(
      `/purchase_orders/${order.id}/receive/`,
    )

    success.value =
      response.data?.message ||
      `Purchase order #${order.id} received successfully.`

    await refreshAll()
  } catch (err: any) {
    error.value =
      err.response?.data?.message ||
      err.response?.data?.detail ||
      'Failed to receive the purchase order.'
  } finally {
    receivingId.value = null
  }
}

async function deleteOrder(order: PurchaseOrder) {
  if (
    !window.confirm(
      `Delete purchase order #${order.id} and its associated details?`,
    )
  ) {
    return
  }

  error.value = ''
  success.value = ''
  deletingId.value = order.id

  try {
    await api.delete(`/purchase_orders/${order.id}/`)

    purchaseOrders.value = purchaseOrders.value.filter(
      item => item.id !== order.id,
    )

    orderDetails.value = orderDetails.value.filter(
      detail => Number(detail.order) !== Number(order.id),
    )

    if (expandedOrderId.value === order.id) {
      expandedOrderId.value = null
    }

    success.value =
      `Purchase order #${order.id} deleted successfully.`
  } catch (err: any) {
    error.value =
      err.response?.data?.message ||
      err.response?.data?.detail ||
      'Failed to delete the purchase order.'
  } finally {
    deletingId.value = null
  }
}

onMounted(async () => {
  await Promise.all([
    fetchOrders(),
    fetchOrderDetails(),
    fetchSuppliers(),
    fetchMedicines(),
  ])
})
</script>

<template>
  <div class="w-full min-w-0 space-y-6 overflow-y-auto pb-6 scrollbar-hide">
    <!-- Header -->
    <div
      class="relative flex flex-col gap-4 overflow-hidden rounded-3xl border border-slate-200/85 bg-white p-7 shadow-sm sm:flex-row sm:items-center sm:justify-between"
    >
      <div
        class="pointer-events-none absolute right-0 top-0 h-32 w-32 rounded-bl-full bg-gradient-to-br from-[#0AD1C8]/10 to-[#80ED99]/20"
      ></div>

      <div class="relative z-10 space-y-1">
        <h1 class="text-2xl font-extrabold tracking-tight text-[#213A57]">
          Purchase Orders &amp; Details
        </h1>

        <p class="text-xs font-medium text-slate-500">
          Manage supplier orders, medicine quantities, costs, and deliveries.
        </p>
      </div>

      <button
        type="button"
        @click="openModal"
        class="relative z-10 flex items-center gap-2 rounded-2xl bg-gradient-to-r from-[#0B6477] to-[#14919B] px-5 py-3 text-xs font-bold text-white shadow-lg shadow-[#14919B]/20 transition hover:-translate-y-0.5 hover:opacity-90"
      >
        <i class="fa-solid fa-plus"></i>
        Create Purchase Order
      </button>
    </div>

    <!-- Messages -->
    <div
      v-if="success"
      class="whitespace-pre-line rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700"
    >
      {{ success }}
    </div>

    <div
      v-if="error"
      class="whitespace-pre-line rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-600"
    >
      {{ error }}
    </div>

    <!-- Purchase Orders Table -->
    <div class="space-y-4 rounded-3xl border border-slate-200/80 bg-white p-6 shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead
            class="border-b border-slate-100 bg-slate-50/80 text-[10px] font-extrabold uppercase tracking-wider text-slate-500"
          >
            <tr>
              <th class="p-4">PO ID</th>
              <th class="p-4">Supplier</th>
              <th class="p-4">Order Date</th>
              <th class="p-4">Total Amount</th>
              <th class="p-4">Status</th>
              <th class="p-4 text-right">Actions</th>
            </tr>
          </thead>

          <tbody class="divide-y divide-slate-100">
            <tr v-if="loading">
              <td colspan="6" class="p-8 text-center text-slate-500">
                <i class="fa-solid fa-spinner fa-spin mr-2"></i>
                Loading purchase orders...
              </td>
            </tr>

            <tr v-else-if="purchaseOrders.length === 0">
              <td colspan="6" class="p-8 text-center text-slate-500">
                No purchase orders found.
              </td>
            </tr>

            <template v-else>
              <template
                v-for="po in purchaseOrders"
                :key="po.id"
              >
                <tr class="transition-colors hover:bg-slate-50/60">
                  <td class="p-4 font-mono font-bold text-slate-700">
                    #PO-{{ po.id }}
                  </td>

                  <td class="p-4 font-semibold text-slate-900">
                    {{ po.supplier_name || supplierName(po.supplier) }}
                  </td>

                  <td class="p-4 text-xs text-slate-600">
                    {{ formatDate(po.order_date) }}
                  </td>

                  <td class="p-4 font-extrabold text-[#0B6477]">
                    {{ formatCurrency(po.total_amount) }}
                  </td>

                  <td class="p-4">
                    <span
                      class="rounded-full border px-3 py-1 text-xs font-bold"
                      :class="statusClass(po.status)"
                    >
                      {{ displayStatus(po.status) }}
                    </span>
                  </td>

                  <td class="p-4">
                    <div class="flex flex-wrap justify-end gap-2">
                      <button
                        type="button"
                        @click="toggleDetails(po.id)"
                        class="rounded-xl bg-sky-50 px-3 py-1.5 text-xs font-semibold text-sky-700 transition hover:bg-sky-100"
                      >
                        {{
                          expandedOrderId === po.id
                            ? 'Hide Details'
                            : 'Details'
                        }}
                      </button>

                      <button
                        v-if="!po.stock_received && po.status !== 'CANCELLED'"
                        type="button"
                        @click="receiveOrder(po)"
                        :disabled="receivingId === po.id"
                        class="rounded-xl bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 transition hover:bg-emerald-100 disabled:opacity-50"
                      >
                        {{
                          receivingId === po.id
                            ? 'Receiving...'
                            : 'Receive'
                        }}
                      </button>

                      <button
                        type="button"
                        @click="deleteOrder(po)"
                        :disabled="deletingId === po.id"
                        class="rounded-xl bg-rose-50 px-3 py-1.5 text-xs font-semibold text-rose-600 transition hover:bg-rose-100 disabled:opacity-50"
                      >
                        {{
                          deletingId === po.id
                            ? 'Deleting...'
                            : 'Delete'
                        }}
                      </button>
                    </div>
                  </td>
                </tr>

                <!-- Order Details -->
                <tr v-if="expandedOrderId === po.id">
                  <td colspan="6" class="bg-slate-50/70 p-4">
                    <div class="rounded-2xl border border-slate-200 bg-white p-4">
                      <h3 class="mb-3 font-bold text-[#213A57]">
                        Details for PO-{{ po.id }}
                      </h3>

                      <div
                        v-if="detailsLoadingId === po.id"
                        class="py-4 text-center text-xs text-slate-500"
                      >
                        Loading order details...
                      </div>

                      <div
                        v-else-if="detailsForOrder(po.id).length === 0"
                        class="py-4 text-center text-xs text-slate-500"
                      >
                        No medicine details were found for this order.
                      </div>

                      <div v-else class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                          <thead class="text-slate-500">
                            <tr>
                              <th class="p-3">Medicine</th>
                              <th class="p-3">Quantity</th>
                              <th class="p-3">Unit Cost</th>
                              <th class="p-3">Subtotal</th>
                            </tr>
                          </thead>

                          <tbody class="divide-y divide-slate-100">
                            <tr
                              v-for="detail in detailsForOrder(po.id)"
                              :key="detail.id"
                            >
                              <td class="p-3 font-semibold text-slate-800">
                                {{ medicineName(detail.medicine) }}
                              </td>

                              <td class="p-3">
                                {{ detail.quantity_order }}
                              </td>

                              <td class="p-3">
                                {{ formatCurrency(detail.unit_cost) }}
                              </td>

                              <td class="p-3 font-bold text-[#0B6477]">
                                {{ formatCurrency(detail.subtotal) }}
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </template>
          </tbody>
        </table>
      </div>

      <div class="flex justify-end border-t border-slate-100 pt-4">
        <button
          type="button"
          @click="refreshAll"
          :disabled="loading"
          class="rounded-xl bg-slate-100 px-4 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-200 disabled:opacity-50"
        >
          <i class="fa-solid fa-rotate-right mr-1"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Create Purchase Order Modal -->
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
            Create Purchase Order
          </h3>

          <button
            type="button"
            @click="closeModal"
            :disabled="saving"
            class="text-slate-400 transition hover:text-slate-600 disabled:opacity-50"
          >
            <i class="fa-solid fa-xmark text-lg"></i>
          </button>
        </div>

        <form @submit.prevent="submitForm" class="space-y-4">
          <!-- Supplier -->
          <div>
            <label class="mb-1 block text-xs font-bold text-slate-600">
              Supplier
            </label>

            <select
              v-model.number="form.supplier"
              required
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-[#14919B] focus:ring-2 focus:ring-[#14919B]/10"
            >
              <option :value="0" disabled>
                Select a supplier
              </option>

              <option
                v-for="supplier in suppliers"
                :key="supplier.id"
                :value="supplier.id"
              >
                {{ supplier.supplier_name }}
              </option>
            </select>

            <p
              v-if="suppliers.length === 0"
              class="mt-1 text-xs text-amber-600"
            >
              No suppliers loaded. Check the suppliers API.
            </p>
          </div>

          <!-- Medicine Autocomplete -->
          <div class="relative">
            <label class="mb-1 block text-xs font-bold text-slate-600">
              Medicine
            </label>

            <input
              v-model="medicineInput"
              @input="onMedicineInput"
              @focus="showSuggestions = true"
              required
              type="text"
              autocomplete="off"
              placeholder="Type a medicine name..."
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-[#14919B] focus:ring-2 focus:ring-[#14919B]/10"
            />

            <ul
              v-if="showSuggestions && filteredMedicines.length > 0"
              class="absolute left-0 right-0 z-20 mt-1 max-h-48 overflow-y-auto rounded-2xl border border-slate-200 bg-white shadow-lg"
            >
              <li
                v-for="medicine in filteredMedicines"
                :key="medicine.id"
                @click="selectMedicine(medicine)"
                class="flex cursor-pointer items-center justify-between px-4 py-2.5 text-xs text-slate-700 hover:bg-slate-100"
              >
                <span class="font-bold">
                  {{ medicine.medicine_name }}
                </span>

                <span class="text-[10px] text-slate-400">
                  {{ medicine.strength || '' }}
                </span>
              </li>
            </ul>

            <p
              v-if="medicineInput && !form.medicine"
              class="mt-1 text-xs text-amber-600"
            >
              Select a medicine from the suggestions.
            </p>

            <p
              v-if="medicines.length === 0"
              class="mt-1 text-xs text-amber-600"
            >
              No medicines loaded. Check the medicines API.
            </p>
          </div>

          <!-- Quantity -->
          <div>
            <label class="mb-1 block text-xs font-bold text-slate-600">
              Quantity Order
            </label>

            <input
              v-model.number="form.quantity_order"
              required
              type="number"
              min="1"
              step="1"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-[#14919B]"
            />
          </div>

          <!-- Unit Cost -->
          <div>
            <label class="mb-1 block text-xs font-bold text-slate-600">
              Unit Cost (₱)
            </label>

            <input
              v-model.number="form.unit_cost"
              required
              type="number"
              min="0"
              step="0.01"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-[#14919B]"
            />
          </div>

          <!-- Estimated Total -->
          <div class="rounded-xl bg-slate-50 p-4">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-slate-500">
                Estimated Total
              </span>

              <span class="text-lg font-extrabold text-[#0B6477]">
                {{ formatCurrency(estimatedTotal) }}
              </span>
            </div>

            <p class="mt-1 text-[10px] text-slate-400">
              Quantity × unit cost
            </p>
          </div>

          <!-- Initial Status -->
          <div>
            <label class="mb-1 block text-xs font-bold text-slate-600">
              Status
            </label>

            <select
              v-model="form.status"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-[#14919B]"
            >
              <option value="PENDING">Pending</option>
              <option value="APPROVED">Approved</option>
            </select>
          </div>

          <!-- Validation Feedback -->
          <div
            v-if="!canSubmit && !saving"
            class="rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-700"
          >
            <p class="mb-1 font-bold">
              Complete the required fields:
            </p>

            <ul class="list-inside list-disc space-y-1">
              <li v-if="!Number.isInteger(Number(form.supplier)) || Number(form.supplier) <= 0">
                Select a supplier.
              </li>

              <li v-if="!Number.isInteger(Number(form.medicine)) || Number(form.medicine) <= 0">
                Select a medicine from the suggestions.
              </li>

              <li v-if="!Number.isInteger(Number(form.quantity_order)) || Number(form.quantity_order) <= 0">
                Enter a positive whole-number quantity.
              </li>

              <li v-if="!Number.isFinite(Number(form.unit_cost)) || Number(form.unit_cost) < 0">
                Enter a valid unit cost.
              </li>
            </ul>
          </div>

          <!-- Actions -->
          <div class="flex justify-end gap-3 border-t border-slate-100 pt-3">
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
              :disabled="!canSubmit"
              class="rounded-xl bg-gradient-to-r from-[#0B6477] to-[#14919B] px-4 py-2 text-xs font-bold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <i
                v-if="saving"
                class="fa-solid fa-spinner fa-spin mr-1"
              ></i>

              {{ saving ? 'Creating...' : 'Create Order' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
