import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '@/services/api'

export interface User {
  id: number
  username: string
  full_name: string
  role: 'ADMIN' | 'STAFF'
}

interface LoginResponse {
  message: string
  access: string
  refresh: string
  user: User
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isRestoring = ref(false)

  const isAuthenticated = computed(() =>
    Boolean(localStorage.getItem('access_token'))
  )

  const isAdmin = computed(() =>
    user.value?.role?.trim().toUpperCase() === 'ADMIN'
  )

  async function login(username: string, password: string) {
    const { data } = await api.post<LoginResponse>(
      '/accounts/login/',
      { username, password }
    )

    const normalizedUser: User = {
      ...data.user,
      role: data.user.role?.trim().toUpperCase() as User['role'],
    }

    if (!['ADMIN', 'STAFF'].includes(normalizedUser.role)) {
      throw new Error(`Invalid user role: ${data.user.role}`)
    }

    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    localStorage.setItem('user', JSON.stringify(normalizedUser))

    user.value = normalizedUser
  }

  function restoreSession() {
    isRestoring.value = true

    try {
      const savedUser = localStorage.getItem('user')

      if (!savedUser || !localStorage.getItem('access_token')) {
        user.value = null
        return
      }

      const parsedUser = JSON.parse(savedUser)

      const role = String(parsedUser?.role ?? '')
        .trim()
        .toUpperCase()

      if (
        parsedUser &&
        typeof parsedUser.id === 'number' &&
        typeof parsedUser.username === 'string' &&
        ['ADMIN', 'STAFF'].includes(role)
      ) {
        user.value = {
          ...parsedUser,
          role: role as User['role'],
        }

        localStorage.setItem('user', JSON.stringify(user.value))
      } else {
        logout()
      }
    } catch {
      logout()
    } finally {
      isRestoring.value = false
    }
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    user.value = null
  }

  return {
    user,
    isAuthenticated,
    isAdmin,
    isRestoring,
    login,
    restoreSession,
    logout,
  }
})
