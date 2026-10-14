<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const showPassword = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true

  try {
    // Login through the Pinia auth store.
    // This saves the tokens and user information.
    await auth.login(username.value, password.value)

    // Redirect after successful login.
    await router.replace('/dashboard')
  } catch (err: any) {
    error.value =
      err.response?.data?.error ||
      err.response?.data?.detail ||
      err.message ||
      'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>


<template>
  <main
    class="min-h-screen w-full flex items-center justify-center
    bg-gradient-to-br from-[#80ED99]/20 via-[#0AD1C8]/10
    to-[#213A57]/15 p-4 font-sans"
  >
    <section
      class="w-full max-w-4xl bg-white rounded-3xl shadow-2xl
      overflow-hidden flex flex-col md:flex-row min-h-[540px]
      border border-white/60"
    >
      <!-- LEFT PANEL -->
      <div
        class="relative overflow-hidden md:w-1/2
        bg-gradient-to-br from-[#213A57] via-[#0B6477]
        to-[#14919B] text-white p-8 md:p-12
        flex flex-col justify-between"
      >
        <div class="relative z-10 space-y-4">
          <div class="flex items-center gap-3 mb-8">
            <div
              class="grid size-12 place-items-center rounded-xl
              bg-[#0AD1C8] text-[#213A57] text-2xl font-bold"
            >
              M
            </div>

            <div>
              <p class="text-xl font-bold tracking-wide">
                MediStock
              </p>
              <p class="text-xs text-white/70">
                Pharmacy Inventory
              </p>
            </div>
          </div>

          <span
            class="text-xs tracking-widest font-semibold uppercase
            text-[#80ED99] flex items-center gap-2"
          >
            <span
              class="w-2 h-2 rounded-full bg-[#0AD1C8] animate-pulse"
            ></span>
            Connected Care, Organised
          </span>

          <h1
            class="text-3xl md:text-4xl font-serif font-bold
            tracking-wide leading-tight text-white"
          >
            Pharmacy Management System
          </h1>

          <p class="text-sm text-[#80ED99]/90 leading-relaxed max-w-sm">
            A focused workspace for medicines, suppliers, stock,
            and purchase orders.
          </p>
        </div>

        <div class="relative z-10 space-y-3 text-xs text-[#80ED99]/90 pt-10">
          <p class="flex items-center gap-2 font-medium">
            <svg
              class="w-4 h-4 text-[#0AD1C8] shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Clear operational oversight
          </p>

          <p class="flex items-center gap-2 font-medium">
            <svg
              class="w-4 h-4 text-[#0AD1C8] shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
              />
            </svg>
            Medicines and stock in one workspace
          </p>

          <p class="flex items-center gap-2 font-medium">
            <svg
              class="w-4 h-4 text-[#0AD1C8] shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4l3 2m6-2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Efficient inventory management
          </p>
        </div>

        <!-- DECORATIVE WATERMARK -->
        <div
          class="absolute -bottom-10 -right-10 pointer-events-none
          opacity-10 text-[#0AD1C8]"
          aria-hidden="true"
        >
          <svg
            width="280"
            height="280"
            viewBox="0 0 100 100"
            fill="currentColor"
          >
            <path d="M35 0h30v35h35v30H65v35H35V65H0V35h35Z" />
          </svg>
        </div>
      </div>

      <!-- RIGHT PANEL: LOGIN FORM -->
      <div
        class="md:w-1/2 bg-white p-8 md:p-12
        flex flex-col justify-center"
      >
        <div class="max-w-sm w-full mx-auto space-y-6">
          <div>
            <p
              class="text-xs font-bold uppercase tracking-[0.2em]
              text-[#0B6477] mb-2"
            >
              Secure Access
            </p>

            <h2 class="text-2xl font-serif font-bold text-[#213A57]">
              Welcome back
            </h2>

            <p class="text-xs text-slate-500 mt-2 leading-relaxed">
              Enter your credentials to access the workspace.
            </p>
          </div>

          <form
            @submit.prevent="handleLogin"
            class="space-y-4"
          >
            <!-- USERNAME -->
            <div class="space-y-1.5">
              <label
                for="username"
                class="block text-xs font-bold text-[#213A57]"
              >
                Username
              </label>

              <div class="relative">
                <div
                  class="absolute inset-y-0 left-0 pl-3.5
                  flex items-center pointer-events-none text-[#0B6477]"
                >
                  <svg
                    class="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                </div>

                <input
                  id="username"
                  v-model.trim="username"
                  type="text"
                  autocomplete="username"
                  required
                  placeholder="Enter your username"
                  class="w-full pl-10 pr-4 py-3 bg-[#80ED99]/15
                  border border-[#0AD1C8]/40 rounded-xl
                  text-sm text-[#213A57] font-medium
                  focus:outline-none focus:ring-2 focus:ring-[#0AD1C8]
                  focus:border-[#0B6477] transition
                  placeholder:text-slate-400"
                />
              </div>
            </div>

            <!-- PASSWORD -->
            <div class="space-y-1.5">
              <label
                for="password"
                class="block text-xs font-bold text-[#213A57]"
              >
                Password
              </label>

              <div class="relative">
                <div
                  class="absolute inset-y-0 left-0 pl-3.5
                  flex items-center pointer-events-none text-[#0B6477]"
                >
                  <svg
                    class="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                  </svg>
                </div>

                <input
                  id="password"
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  autocomplete="current-password"
                  required
                  placeholder="Enter your password"
                  class="w-full pl-10 pr-11 py-3 bg-[#80ED99]/15
                  border border-[#0AD1C8]/40 rounded-xl
                  text-sm text-[#213A57] font-medium
                  focus:outline-none focus:ring-2 focus:ring-[#0AD1C8]
                  focus:border-[#0B6477] transition
                  placeholder:text-slate-400"
                />

                <!-- PASSWORD VISIBILITY TOGGLE -->
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute inset-y-0 right-0 px-3.5
                  flex items-center text-[#0B6477]
                  hover:text-[#213A57] transition"
                  :aria-label="
                    showPassword ? 'Hide password' : 'Show password'
                  "
                  :aria-pressed="showPassword"
                >
                  <svg
                    v-if="!showPassword"
                    class="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                    />
                  </svg>

                  <svg
                    v-else
                    class="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858-5.908A8.982 8.982 0 0112 5c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m-1.412-1.412a3 3 0 10-4.243-4.243m4.243 4.243L3 3l18 18"
                    />
                  </svg>
                </button>
              </div>
            </div>

            <!-- ERROR MESSAGE -->
            <div
              v-if="error"
              role="alert"
              aria-live="polite"
              class="rounded-xl border border-red-200 bg-red-50
              px-4 py-3 text-sm text-red-700"
            >
              {{ error }}
            </div>

            <!-- SIGN IN BUTTON -->
            <button
              type="submit"
              :disabled="loading"
              class="w-full bg-[#0B6477] hover:bg-[#213A57]
              disabled:opacity-60 disabled:cursor-not-allowed
              text-white font-semibold py-3 px-4 rounded-xl
              transition duration-300 shadow-md shadow-[#0B6477]/20
              text-sm flex items-center justify-center gap-2
              group active:scale-[0.99] mt-2"
            >
              <span>{{ loading ? 'Signing in...' : 'Sign in' }}</span>

              <svg
                v-if="!loading"
                class="w-4 h-4 transform group-hover:translate-x-1 transition duration-200"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M14 5l7 7m0 0l-7 7m7-7H3"
                />
              </svg>

              <svg
                v-else
                class="w-4 h-4 animate-spin"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                />
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
            </button>
          </form>

          <!-- FOOTER -->
          <div class="pt-4 border-t border-slate-100">
            <p class="text-center text-xs text-slate-500 leading-relaxed">
              Only authorized
              <span class="font-semibold text-[#0B6477]">ADMIN</span>
              and
              <span class="font-semibold text-[#0B6477]">STAFF</span>
              accounts can sign in.
            </p>

            <p class="text-center text-[10px] text-slate-400 mt-3">
              MediStock Pharmacy Inventory System
            </p>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>
