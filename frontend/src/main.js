import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import './assets/css/styles.css'

// Import global components (optional)
// import BaseButton from '@/components/BaseButton.vue'
// import BaseCard from '@/components/BaseCard.vue'

// Create the Vue app instance
const app = createApp(App)

// Register global components (optional)
// app.component('BaseButton', BaseButton)
// app.component('BaseCard', BaseCard)

// Add global properties (optional)
app.config.globalProperties.$appName = 'Mini CRM'
app.config.globalProperties.$version = '1.0.0'

// Add global error handler
app.config.errorHandler = (err, vm, info) => {
  console.error('Global Vue error:', err)
  console.error('Component:', vm)
  console.error('Info:', info)
  
  // You could send this to an error tracking service
  // Sentry.captureException(err, { extra: { vm, info } })
}

// Add global warn handler
app.config.warnHandler = (msg, vm, trace) => {
  console.warn('Vue warning:', msg)
  console.warn('Component:', vm)
  console.warn('Trace:', trace)
}

// Register plugins
app.use(router)
app.use(vuetify)

// Mount the app
app.mount('#app')

// Optional: Add performance monitoring in development
if (import.meta.env.DEV) {
  // Log performance info
  window.addEventListener('load', () => {
    const timing = performance.timing
    const loadTime = timing.loadEventEnd - timing.navigationStart
    console.log(`App loaded in ${loadTime}ms`)
  })
}

// Optional: Add global keyboard shortcuts
window.addEventListener('keydown', (event) => {
  // Global Ctrl+S to save (prevent default browser save)
  if ((event.ctrlKey || event.metaKey) && event.key === 's') {
    event.preventDefault()
    // You could emit a global event here
    // app.config.globalProperties.$emitter.emit('global-save')
  }
})

// Optional: Add service worker for PWA
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(registration => {
        console.log('ServiceWorker registration successful with scope:', registration.scope)
      })
      .catch(error => {
        console.log('ServiceWorker registration failed:', error)
      })
  })
}

// Optional: Add theme persistence
const savedTheme = localStorage.getItem('theme')
if (savedTheme) {
  // Apply saved theme
  document.documentElement.setAttribute('data-theme', savedTheme)
}

// Optional: Global event emitter (if not using Vuex/Pinia)
// const emitter = mitt()
// app.config.globalProperties.$emitter = emitter
