import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store' // If using Vuex/Pinia

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { 
      requiresGuest: true,
      title: 'Login - CRM',
      layout: 'auth'
    }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Dashboard - CRM',
      breadcrumb: 'Dashboard'
    }
  },
  {
    path: '/contacts',
    name: 'Contacts',
    component: () => import('@/views/ContactsView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Contacts - CRM',
      breadcrumb: 'Contacts'
    }
  },
  {
    path: '/contacts/create',
    name: 'ContactCreate',
    component: () => import('@/views/ContactFormView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Create Contact - CRM',
      breadcrumb: [{ name: 'Contacts', to: '/contacts' }, 'Create']
    }
  },
  {
    path: '/contacts/:id',
    name: 'ContactDetail',
    component: () => import('@/views/ContactDetailView.vue'),
    props: true,
    meta: { 
      requiresAuth: true,
      title: 'Contact Details - CRM'
    }
  },
  {
    path: '/contacts/:id/edit',
    name: 'ContactEdit',
    component: () => import('@/views/ContactFormView.vue'),
    props: true,
    meta: { 
      requiresAuth: true,
      title: 'Edit Contact - CRM'
    }
  },
  {
    path: '/companies',
    name: 'Companies',
    component: () => import('@/views/CompaniesView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Companies - CRM',
      breadcrumb: 'Companies'
    }
  },
  {
    path: '/deals',
    name: 'Deals',
    component: () => import('@/views/DealsView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Deals - CRM',
      breadcrumb: 'Deals'
    }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/TasksView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Tasks - CRM',
      breadcrumb: 'Tasks'
    }
  },
  // Settings/Profile Routes
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Settings - CRM'
    }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'My Profile - CRM'
    }
  },
  // 404 Catch-all
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { 
      title: '404 - Page Not Found'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // Return to saved position
    if (savedPosition) {
      return savedPosition
    }
    
    // Scroll to element if hash is present
    if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth'
      }
    }
    
    // Default to top of page
    return { top: 0, left: 0 }
  }
})

// Global Navigation Guards
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  const user = localStorage.getItem('user')
  const isAuthenticated = !!token && !!user

  // Set page title
  document.title = to.meta.title || 'CRM System'

  // Auth check for protected routes
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Store the intended URL for redirect after login
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
    return
  }

  // Guest check for login/register pages
  if (to.meta.requiresGuest && isAuthenticated) {
    next('/')
    return
  }

  // Optional: Validate token for protected routes
  if (to.meta.requiresAuth && isAuthenticated) {
    // You could add token validation logic here
    // For example, check if token is expired
    const tokenExpiry = localStorage.getItem('token_expiry')
    if (tokenExpiry && new Date(tokenExpiry) < new Date()) {
      // Token expired
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('token_expiry')
      next({
        path: '/login',
        query: { 
          redirect: to.fullPath,
          error: 'session_expired'
        }
      })
      return
    }
  }

  next()
})

// Optional: Global afterEach hook
router.afterEach((to, from) => {
  // Analytics tracking
  if (typeof gtag !== 'undefined') {
    gtag('config', 'G-XXXXXXXXXX', {
      page_path: to.path,
      page_title: to.meta.title || 'CRM System'
    })
  }
  
  // Reset scroll for specific routes
  if (to.meta.resetScroll) {
    window.scrollTo(0, 0)
  }
})

export default router
