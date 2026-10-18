
<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

interface Account {
  id: number
  account_id?: number
  username: string
  full_name: string
  role: string | number
  role_id?: number
  is_active?: boolean
}

const auth = useAuthStore()

const accounts = ref<Account[]>([])
const loading = ref(false)
const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showAccountModal = ref(false)
const showPassword = ref(false)
const search = ref('')

const form = reactive({
  username: '',
  full_name: '',
  password: '',
})

const isAdmin = computed(() =>
  String(auth.user?.role ?? '').toUpperCase() === 'ADMIN'
)

const currentUserId = computed(() => auth.user?.id)

const getId = (account: Account) => account.id ?? account.account_id ?? 0

const isAccountAdmin = (account: Account) =>
  String(account.role).toUpperCase() === 'ADMIN' ||
  account.role_id === 1 ||
  Number(account.role) === 1

const filteredAccounts = computed(() => {
  const term = search.value.trim().toLowerCase()

  if (!term) return accounts.value

  return accounts.value.filter(account =>
    [account.full_name, account.username, String(account.role)]
      .some(value => value?.toLowerCase().includes(term))
  )
})

async function loadAccounts() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await api.get('/accounts/')
    const data = response.data

    accounts.value = Array.isArray(data)
      ? data
      : Array.isArray(data.results)
        ? data.results
        : []
  } catch (error: any) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to load accounts. Check your API permissions and endpoint.'
  } finally {
    loading.value = false
  }
}

async function submitAccount() {
  if (!isAdmin.value) return

  errorMessage.value = ''
  successMessage.value = ''

  if (!form.username.trim() || !form.full_name.trim() || !form.password) {
    errorMessage.value = 'Please complete all fields.'
    return
  }

  submitting.value = true

  try {
    await api.post('/accounts/', {
      username: form.username.trim(),
      full_name: form.full_name.trim(),
      password: form.password,
      role: 'STAFF',
    })

    successMessage.value = 'Staff account created successfully.'
    Object.assign(form, {
      username: '',
      full_name: '',
      password: '',
    })
    showAccountModal.value = false
    await loadAccounts()
  } catch (error: any) {
    const data = error.response?.data
    errorMessage.value = typeof data === 'object'
      ? Object.entries(data)
          .map(([field, message]) => `${field}: ${
            Array.isArray(message) ? message.join(', ') : String(message)
          }`)
          .join(' ')
      : 'Unable to create the account. Please try again.'
  } finally {
    submitting.value = false
  }
}

async function deleteAccount(account: Account) {
  if (!isAdmin.value) return

  const id = getId(account)

  if (!id || id === currentUserId.value) return

  if (!window.confirm(`Delete the account for ${account.full_name}?`)) return

  errorMessage.value = ''
  successMessage.value = ''

  try {
    await api.delete(`/accounts/${id}/`)
    successMessage.value = 'Account deleted successfully.'
    await loadAccounts()
  } catch (error: any) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to delete this account. Verify that your Django API supports DELETE.'
  }
}

onMounted(loadAccounts)
</script>

<template>
  <div class="w-full space-y-6 overflow-y-auto pb-6">
    <!-- Header -->
    <section
      class="relative flex flex-col gap-4 overflow-hidden rounded-3xl border border-slate-200/80 bg-white p-7 shadow-sm sm:flex-row sm:items-center sm:justify-between"
    >
      <div
        class="pointer-events-none absolute right-0 top-0 h-32 w-32 rounded-bl-full bg-gradient-to-br from-[#0AD1C8]/10 to-[#80ED99]/20"
      />

      <div class="relative z-10 space-y-1">
        <p class="text-xs font-bold uppercase tracking-[0.18em] text-[#14919B]">
          Administration
        </p>
        <h1 class="text-2xl font-extrabold tracking-tight text-[#213A57]">
          Staff Account Management
        </h1>
        <p class="text-xs font-medium text-slate-500">
          Create and manage pharmacy staff accounts.
        </p>
      </div>

      <button
        v-if="isAdmin"
        type="button"
        @click="showAccountModal = true"
        class="relative z-10 flex items-center justify-center gap-2.5 rounded-2xl bg-gradient-to-r from-[#0B6477] to-[#14919B] px-5 py-3 text-xs font-bold text-white shadow-lg shadow-[#14919B]/20 transition hover:-translate-y-0.5 hover:opacity-95"
      >
        <span class="text-base">＋</span>
        Create Staff Account
      </button>
    </section>

    <!-- Feedback -->
    <div
      v-if="errorMessage"
      role="alert"
      class="flex items-start justify-between gap-3 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700"
    >
      <span>{{ errorMessage }}</span>
      <button @click="errorMessage = ''" aria-label="Dismiss error">✕</button>
    </div>

    <div
      v-if="successMessage"
      role="status"
      class="flex items-center justify-between gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700"
    >
      <span>{{ successMessage }}</span>
      <button @click="successMessage = ''" aria-label="Dismiss message">✕</button>
    </div>

    <!-- Staff restriction -->
    <div
      v-if="!isAdmin"
      class="flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800"
    >
      <span class="text-lg">⚠</span>
      <div>
        <p class="font-bold">Restricted Access</p>
        <p class="mt-1">
          You are signed in as a staff member. Only an administrator can
          create or delete accounts.
        </p>
      </div>
    </div>

    <!-- Account table -->
    <section
      class="space-y-5 rounded-3xl border border-slate-200/80 bg-white p-5 shadow-sm sm:p-6"
    >
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 class="text-lg font-extrabold text-[#213A57]">System Accounts</h2>
          <p class="mt-1 text-xs text-slate-500">
            {{ accounts.length }} account(s) registered
          </p>
        </div>

        <input
          v-model="search"
          type="search"
          placeholder="Search name or username..."
          class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-xs outline-none transition focus:border-[#14919B] focus:ring-2 focus:ring-[#14919B]/15 sm:max-w-xs"
        />
      </div>

      <div class="overflow-x-auto">
        <table class="w-full min-w-[700px] text-left text-sm">
          <thead
            class="border-b border-slate-100 bg-slate-50/80 text-[10px] font-extrabold uppercase tracking-wider text-slate-500"
          >
            <tr>
              <th class="p-4">Account ID</th>
              <th class="p-4">Staff Member</th>
              <th class="p-4">Username</th>
              <th class="p-4">Role</th>
              <th class="p-4">Password Security</th>
              <th v-if="isAdmin" class="p-4 text-right">Actions</th>
            </tr>
          </thead>

          <tbody class="divide-y divide-slate-100">
            <tr v-if="loading">
              <td :colspan="isAdmin ? 6 : 5" class="p-8 text-center text-sm text-slate-500">
                Loading accounts...
              </td>
            </tr>

            <tr v-else-if="filteredAccounts.length === 0">
              <td :colspan="isAdmin ? 6 : 5" class="p-8 text-center text-sm text-slate-500">
                No accounts found.
              </td>
            </tr>

            <tr
              v-for="account in filteredAccounts"
              :key="getId(account)"
              class="transition-colors hover:bg-slate-50/70"
            >
              <td class="p-4 font-mono text-xs text-slate-500">
                #{{ getId(account) }}
              </td>

              <td class="p-4">
                <div class="flex items-center gap-3">
                  <div
                    class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-[#14919B]/20 bg-[#14919B]/10 text-xs font-extrabold text-[#14919B]"
                  >
                    {{ (account.full_name || account.username || '?').charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <p class="font-bold text-slate-900">
                      {{ account.full_name || 'Name not provided' }}
                    </p>
                    <p class="mt-0.5 text-[10px] text-slate-400">
                      {{ account.is_active === false ? 'Inactive' : 'Account registered' }}
                    </p>
                  </div>
                </div>
              </td>

              <td class="p-4 text-xs text-slate-600">
                {{ account.username }}
              </td>

              <td class="p-4">
                <span
                  class="inline-block rounded-full px-3 py-1 text-[10px] font-extrabold"
                  :class="isAccountAdmin(account)
                    ? 'bg-[#213A57] text-white'
                    : 'bg-slate-100 text-slate-700'"
                >
                  {{ isAccountAdmin(account) ? 'ADMIN' : 'STAFF' }}
                </span>
              </td>

              <td class="p-4">
                <span
                  class="inline-flex items-center gap-2 rounded-xl bg-emerald-50 px-3 py-2 text-[10px] font-bold text-emerald-700"
                >
                  <span>🔒</span>
                  Password protected
                </span>
              </td>

              <td v-if="isAdmin" class="p-4 text-right">
                <span
                  v-if="getId(account) === currentUserId"
                  class="text-xs italic text-slate-400"
                >
                  Current User
                </span>

                <button
                  v-else
                  type="button"
                  @click="deleteAccount(account)"
                  class="inline-flex items-center gap-1.5 rounded-xl bg-rose-50 px-3.5 py-2 text-xs font-semibold text-rose-600 transition hover:bg-rose-100"
                >
                  <span>✕</span>
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Create account modal -->
    <div
      v-if="showAccountModal && isAdmin"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm"
      @click.self="showAccountModal = false"
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="account-modal-title"
        class="w-full max-w-md space-y-5 rounded-3xl border border-slate-100 bg-white p-6 shadow-xl"
      >
        <div class="flex items-center justify-between border-b border-slate-100 pb-4">
          <div>
            <p class="text-[10px] font-bold uppercase tracking-widest text-[#14919B]">
              New staff member
            </p>
            <h2 id="account-modal-title" class="mt-1 text-lg font-extrabold text-[#213A57]">
              Create Staff Account
            </h2>
          </div>

          <button
            type="button"
            @click="showAccountModal = false"
            class="rounded-xl p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        <form class="space-y-4" @submit.prevent="submitAccount">
          <div>
            <label class="mb-1.5 block text-xs font-bold text-slate-600">
              Full Name
            </label>
            <input
              v-model="form.full_name"
              required
              type="text"
              autocomplete="name"
              placeholder="e.g. Maria Santos"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-3 text-xs outline-none focus:border-[#14919B] focus:ring-2 focus:ring-[#14919B]/15"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-xs font-bold text-slate-600">
              Username
            </label>
            <input
              v-model="form.username"
              required
              type="text"
              autocomplete="username"
              placeholder="Create a username"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-3 text-xs outline-none focus:border-[#14919B] focus:ring-2 focus:ring-[#14919B]/15"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-xs font-bold text-slate-600">
              Password
            </label>
            <div class="relative">
              <input
                v-model="form.password"
                required
                :type="showPassword ? 'text' : 'password'"
                autocomplete="new-password"
                placeholder="Enter a password"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-3 pr-16 text-xs outline-none focus:border-[#14919B] focus:ring-2 focus:ring-[#14919B]/15"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-3 text-xs font-bold text-[#14919B]"
              >
                {{ showPassword ? 'Hide' : 'Show' }}
              </button>
            </div>
          </div>

          <div>
            <label class="mb-1.5 block text-xs font-bold text-slate-600">
              Role Assigned
            </label>
            <input
              disabled
              value="Staff — Standard Access"
              class="w-full cursor-not-allowed rounded-xl border border-slate-200 bg-slate-100 px-3.5 py-3 text-xs font-semibold text-slate-500"
            />
            <p class="mt-1.5 text-[10px] text-slate-400">
              Staff accounts cannot assign themselves administrator privileges.
            </p>
          </div>

          <div class="flex justify-end gap-3 border-t border-slate-100 pt-4">
            <button
              type="button"
              @click="showAccountModal = false"
              class="rounded-xl bg-slate-100 px-4 py-2.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-200"
            >
              Cancel
            </button>

            <button
              type="submit"
              :disabled="submitting"
              class="rounded-xl bg-gradient-to-r from-[#0B6477] to-[#14919B] px-4 py-2.5 text-xs font-bold text-white shadow-sm transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {{ submitting ? 'Creating...' : 'Create Account' }}
            </button>
          </div>
        </form>
      </section>
    </div>
  </div>
</template>
