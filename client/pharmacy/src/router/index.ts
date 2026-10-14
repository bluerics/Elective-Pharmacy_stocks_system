
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import LoginView from '../pages/LoginView.vue'
import DashboardLayout from '../layouts/Dashboard.vue'
import DashboardView from '../pages/DashboardView.vue'
import MedicineView from '../pages/MedicineView.vue'
import AccountView from '../pages/AccountView.vue'
import StockView from '../pages/StockView.vue'
import PurchaseOrderView from '../pages/PurchaseOrderView.vue'
import SupplierView from '../pages/SupplierView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: LoginView,
      meta: { public: true },
    },
    {
      path: '/',
      component: DashboardLayout,
      children: [
        {
          path: '',
          redirect: '/dashboard',
        },
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: DashboardView,
        },
        {
          path: 'medicines',
          name: 'Medicines',
          component: MedicineView,
        },
        {
          path: 'stocks',
          name: 'Stocks',
          component: StockView,
        },
        {
          path: 'purchase_orders',
          name: 'PurchaseOrders',
          component: PurchaseOrderView,
        },
        {
          path: 'suppliers',
          name: 'Suppliers',
          component: SupplierView,
        },
        {
          path: 'accounts',
          name: 'Accounts',
          component: AccountView,
          meta: { adminOnly: true },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/dashboard',
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  auth.restoreSession()

  const token = localStorage.getItem('access_token')

  if (!to.meta.public && !token) {
    return '/login'
  }

  if (to.meta.public && token) {
    return '/dashboard'
  }

  if (
    to.meta.adminOnly &&
    String(auth.user?.role ?? '').toUpperCase() !== 'ADMIN'
  ) {
    return '/dashboard'
  }

  return true
})

export default router
