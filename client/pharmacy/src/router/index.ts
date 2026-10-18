
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
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'Login',
      component: LoginView,
      meta: { public: true },
    },
    {
      path: '/',
      component: DashboardLayout,
      meta: { requiresAuth: true },
      children: [
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
      redirect: '/login',
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  auth.restoreSession()

  const token = localStorage.getItem('access_token')

  // Require authentication for inventory pages.
  if (to.matched.some(record => record.meta.requiresAuth) && !token) {
    return '/login'
  }

  // Restrict Accounts & Roles to admins.
  if (
    to.matched.some(record => record.meta.adminOnly) &&
    !auth.isAdmin
  ) {
    return '/dashboard'
  }

  // Allow /login even if a previous session exists.
  return true
})

export default router
