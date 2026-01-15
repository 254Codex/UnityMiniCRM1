<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const drawer = ref(true)
const rail = ref(false)
const user = ref(null)
const darkMode = ref(false)
const searchQuery = ref('')
const notifications = ref([])

const isAuthenticated = computed(() => !!localStorage.getItem('token'))

const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

// Updated to exclude auth pages
const showLayout = computed(() => {
  const noLayoutRoutes = ['/login', '/register', '/forgot-password']
  return !noLayoutRoutes.includes(route.path)
})

onMounted(() => {
  loadUserData()
  loadNotifications()
  setupKeyboardShortcuts()
  loadThemePreference()
})

onUnmounted(() => {
  cleanupKeyboardShortcuts()
})

// Load user data
const loadUserData = async () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    user.value = JSON.parse(userStr)
  }
  
  if (isAuthenticated.value && (!user.value || !user.value.username)) {
    try {
      const response = await api.users.getProfile()
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
    } catch (error) {
      console.error('Error loading user profile:', error)
    }
  }
}

// Load notifications
const loadNotifications = async () => {
  try {
    // This endpoint may need to be created
    const response = await api.tasks.getMyTasks()
    // Use tasks as notifications for now
    notifications.value = response.data.map(task => ({
      id: task.id,
      title: `Task due: ${task.title}`,
      message: task.description || 'No description',
      timestamp: task.due_date,
      read: task.status === 'completed',
      type: 'task'
    }))
  } catch (error) {
    console.error('Failed to load notifications:', error)
  }
}

// Theme handling
const loadThemePreference = () => {
  const savedTheme = localStorage.getItem('darkMode')
  if (savedTheme) {
    darkMode.value = savedTheme === 'true'
    applyTheme(darkMode.value)
  }
}

const applyTheme = (isDark) => {
  document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light')
}

const toggleDarkMode = () => {
  darkMode.value = !darkMode.value
  localStorage.setItem('darkMode', darkMode.value)
  applyTheme(darkMode.value)
}

// Keyboard shortcuts
const handleKeyPress = (event) => {
  // Global search (Cmd/Ctrl + K)
  if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
    event.preventDefault()
    const searchInput = document.querySelector('.search-field input')
    if (searchInput) searchInput.focus()
    return
  }
  
  // Navigation shortcuts (only when authenticated)
  if (isAuthenticated.value && (event.ctrlKey || event.metaKey)) {
    switch(event.key) {
      case 'd':
        event.preventDefault()
        router.push('/')
        break
      case 'c':
        event.preventDefault()
        router.push('/contacts')
        break
      case 'o':
        event.preventDefault()
        router.push('/companies')
        break
      case 's':
        event.preventDefault()
        router.push('/deals')
        break
      case 't':
        event.preventDefault()
        router.push('/tasks')
        break
      case 'p':
        event.preventDefault()
        router.push('/profile')
        break
    }
  }
}

const setupKeyboardShortcuts = () => {
  window.addEventListener('keydown', handleKeyPress)
}

const cleanupKeyboardShortcuts = () => {
  window.removeEventListener('keydown', handleKeyPress)
}

const menuItems = [
  { 
    title: 'Dashboard', 
    icon: 'mdi-view-dashboard-variant', 
    route: '/',
    description: 'Overview & insights',
    color: '#1976D2',
    gradient: 'linear-gradient(135deg, #1565C0 0%, #0D47A1 100%)',
    shortcut: 'Ctrl+D'
  },
  { 
    title: 'Contacts', 
    icon: 'mdi-account-group', 
    route: '/contacts',
    description: 'Manage contacts',
    color: '#0288D1',
    gradient: 'linear-gradient(135deg, #0288D1 0%, #01579B 100%)',
    shortcut: 'Ctrl+C'
  },
  { 
    title: 'Companies', 
    icon: 'mdi-domain', 
    route: '/companies',
    description: 'Business partners',
    color: '#1976D2',
    gradient: 'linear-gradient(135deg, #1976D2 0%, #0D47A1 100%)',
    shortcut: 'Ctrl+O'
  },
  { 
    title: 'Deals', 
    icon: 'mdi-handshake', 
    route: '/deals',
    description: 'Sales pipeline',
    color: '#0277BD',
    gradient: 'linear-gradient(135deg, #0277BD 0%, #01579B 100%)',
    shortcut: 'Ctrl+S'
  },
  { 
    title: 'Tasks', 
    icon: 'mdi-checkbox-marked-circle', 
    route: '/tasks',
    description: 'Todo & reminders',
    color: '#0288D1',
    gradient: 'linear-gradient(135deg, #039BE5 0%, #01579B 100%)',
    shortcut: 'Ctrl+T'
  },
  { 
    title: 'Profile', 
    icon: 'mdi-account-cog', 
    route: '/profile',
    description: 'Manage your profile',
    color: '#7B1FA2',
    gradient: 'linear-gradient(135deg, #7B1FA2 0%, #4A148C 100%)',
    shortcut: 'Ctrl+P'
  },
]

const handleLogout = async () => {
  try {
    await api.auth.logout()
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    user.value = null
    router.push('/login')
  }
}

const userDisplay = computed(() => {
  if (!user.value) return 'User'
  
  if (user.value.user && user.value.user.first_name && user.value.user.last_name) {
    return `${user.value.user.first_name} ${user.value.user.last_name}`
  }
  
  if (user.value.first_name && user.value.last_name) {
    return `${user.value.first_name} ${user.value.last_name}`
  }
  
  return user.value.username || 'User'
})

const getUserInitials = () => {
  if (!user.value) return 'U'
  
  let firstName = ''
  let lastName = ''
  
  if (user.value.user) {
    firstName = user.value.user.first_name || ''
    lastName = user.value.user.last_name || ''
  } else {
    firstName = user.value.first_name || ''
    lastName = user.value.last_name || ''
  }
  
  if (firstName && lastName) {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
  }
  
  return (user.value.username || 'U').charAt(0).toUpperCase()
}

const getItemGradient = (item) => {
  return route.path === item.route ? item.gradient : 'transparent'
}

const handleSearch = (query) => {
  if (query.trim()) {
    router.push(`/search?q=${encodeURIComponent(query.trim())}`)
  }
}

const quickAdd = {
  contact: () => router.push('/contacts/create'),
  company: () => router.push('/companies/create'),
  deal: () => router.push('/deals/create'),
  task: () => router.push('/tasks/create'),
}

const navigateTo = (path) => {
  router.push(path)
}

// Mark all notifications as read
const markAllAsRead = () => {
  notifications.value.forEach(n => n.read = true)
}
</script>

<template>
  <v-app :theme="darkMode ? 'dark' : 'light'">
    <template v-if="showLayout && isAuthenticated">
      <!-- Premium App Bar -->
      <v-app-bar 
        elevation="0" 
        class="app-bar glass-effect"
        height="80"
      >
        <div class="d-flex align-center w-100 px-4">
          <!-- Logo & Brand -->
          <div class="d-flex align-center">
            <v-btn 
              icon 
              @click="drawer = !drawer"
              class="mr-3"
              variant="text"
              size="large"
            >
              <v-icon>mdi-menu</v-icon>
            </v-btn>
            
            <div class="brand-section d-flex align-center">
              <div class="logo-wrapper">
                <v-icon size="36" class="logo-icon">mdi-office-building</v-icon>
              </div>
              <div class="ml-3 d-none d-md-block">
                <div class="text-h5 font-weight-bold brand-text">Mini CRM</div>
                <div class="text-caption text-grey-darken-1">Customer Success Platform</div>
              </div>
            </div>
          </div>
          
          <v-spacer></v-spacer>
          
          <!-- Search Bar -->
          <div class="search-wrapper mx-4 d-none d-sm-block">
            <v-text-field
              v-model="searchQuery"
              @keyup.enter="handleSearch(searchQuery)"
              prepend-inner-icon="mdi-magnify"
              placeholder="Search contacts, deals, companies..."
              variant="solo"
              density="comfortable"
              hide-details
              flat
              class="search-field"
              bg-color="grey-lighten-4"
            >
              <template v-slot:append-inner>
                <v-chip size="x-small" class="search-shortcut">⌘K</v-chip>
              </template>
            </v-text-field>
          </div>
          
          <v-spacer></v-spacer>
          
          <!-- Actions -->
          <div class="d-flex align-center gap-2">
            <!-- Dark Mode Toggle -->
            <v-btn 
              icon 
              class="action-btn"
              variant="text"
              @click="toggleDarkMode"
              :title="darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
            >
              <v-icon v-if="darkMode">mdi-weather-sunny</v-icon>
              <v-icon v-else>mdi-weather-night</v-icon>
            </v-btn>
            
            <!-- Quick Add -->
            <v-menu offset-y>
              <template v-slot:activator="{ props }">
                <v-btn 
                  icon 
                  v-bind="props"
                  class="action-btn"
                  variant="tonal"
                  color="primary"
                >
                  <v-icon>mdi-plus-circle</v-icon>
                </v-btn>
              </template>
              <v-list min-width="200">
                <v-list-subheader>Quick Add</v-list-subheader>
                <v-list-item 
                  prepend-icon="mdi-account-plus" 
                  title="New Contact" 
                  @click="quickAdd.contact"
                ></v-list-item>
                <v-list-item 
                  prepend-icon="mdi-office-building-plus" 
                  title="New Company" 
                  @click="quickAdd.company"
                ></v-list-item>
                <v-list-item 
                  prepend-icon="mdi-handshake" 
                  title="New Deal" 
                  @click="quickAdd.deal"
                ></v-list-item>
                <v-list-item 
                  prepend-icon="mdi-plus" 
                  title="New Task" 
                  @click="quickAdd.task"
                ></v-list-item>
              </v-list>
            </v-menu>
            
            <!-- Notifications -->
            <v-menu offset-y min-width="350">
              <template v-slot:activator="{ props }">
                <v-btn icon class="action-btn" variant="text" v-bind="props">
                  <v-badge 
                    :content="unreadCount" 
                    :color="unreadCount > 0 ? 'error' : 'transparent'" 
                    offset-x="12" 
                    offset-y="12"
                  >
                    <v-icon>mdi-bell</v-icon>
                  </v-badge>
                </v-btn>
              </template>
              <v-card class="notifications-card">
                <v-card-title class="d-flex justify-space-between align-center pa-4">
                  <span class="text-h6 font-weight-bold">Notifications</span>
                  <v-btn 
                    v-if="unreadCount > 0" 
                    size="small" 
                    variant="text" 
                    @click="markAllAsRead"
                  >
                    Mark all as read
                  </v-btn>
                </v-card-title>
                <v-divider></v-divider>
                <v-list density="compact" class="pa-0">
                  <v-list-item 
                    v-for="notification in notifications.slice(0, 5)" 
                    :key="notification.id"
                    :class="{ 'bg-grey-lighten-4': !notification.read }"
                    @click="navigateTo('/tasks')"
                  >
                    <template v-slot:prepend>
                      <v-icon :color="notification.type === 'task' ? 'primary' : 'warning'">
                        {{ notification.type === 'task' ? 'mdi-check-circle' : 'mdi-alert' }}
                      </v-icon>
                    </template>
                    <v-list-item-title>{{ notification.title }}</v-list-item-title>
                    <v-list-item-subtitle class="text-truncate">
                      {{ notification.message }}
                    </v-list-item-subtitle>
                    <template v-slot:append>
                      <v-chip size="x-small" variant="tonal">
                        {{ formatTimeAgo(notification.timestamp) }}
                      </v-chip>
                    </template>
                  </v-list-item>
                  <v-list-item v-if="notifications.length === 0">
                    <v-list-item-title class="text-grey text-center">
                      No notifications
                    </v-list-item-title>
                  </v-list-item>
                </v-list>
                <v-divider></v-divider>
                <v-card-actions>
                  <v-btn 
                    block 
                    variant="text" 
                    @click="navigateTo('/notifications')"
                    :disabled="notifications.length === 0"
                  >
                    View All Notifications
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-menu>
            
            <!-- User Menu -->
            <v-menu offset-y min-width="280">
              <template v-slot:activator="{ props }">
                <v-btn v-bind="props" variant="flat" class="user-btn px-2" rounded="lg">
                  <v-avatar color="primary" size="40" class="avatar-gradient">
                    <span class="text-white font-weight-bold">{{ getUserInitials() }}</span>
                  </v-avatar>
                  <div class="ml-3 text-left d-none d-lg-block">
                    <div class="text-body-2 font-weight-bold">{{ userDisplay }}</div>
                    <div class="text-caption text-grey">{{ user?.email || user?.user?.email || 'Premium Account' }}</div>
                  </div>
                  <v-icon class="ml-2">mdi-chevron-down</v-icon>
                </v-btn>
              </template>
              <v-card class="user-menu-card">
                <v-card-text class="pa-4">
                  <div class="d-flex align-center mb-3">
                    <v-avatar color="primary" size="56" class="avatar-gradient">
                      <span class="text-white text-h5 font-weight-bold">{{ getUserInitials() }}</span>
                    </v-avatar>
                    <div class="ml-3">
                      <div class="text-h6 font-weight-bold">{{ userDisplay }}</div>
                      <div class="text-caption text-grey">{{ user?.email || user?.user?.email || '' }}</div>
                      <v-chip size="x-small" color="success" class="mt-1">Premium</v-chip>
                    </div>
                  </div>
                  <v-divider class="my-3"></v-divider>
                  <v-list density="compact" class="bg-transparent">
                    <v-list-item 
                      prepend-icon="mdi-account-circle" 
                      title="My Profile" 
                      subtitle="View your details"
                      @click="navigateTo('/profile')"
                    ></v-list-item>
                    <v-list-item 
                      prepend-icon="mdi-cog" 
                      title="Settings" 
                      subtitle="Preferences"
                      @click="navigateTo('/settings')"
                    ></v-list-item>
                    <v-list-item 
                      prepend-icon="mdi-palette" 
                      :title="darkMode ? 'Light Mode' : 'Dark Mode'" 
                      subtitle="Toggle theme"
                      @click="toggleDarkMode"
                    ></v-list-item>
                    <v-divider class="my-2"></v-divider>
                    <v-list-item 
                      @click="handleLogout"
                      prepend-icon="mdi-logout"
                      title="Sign Out"
                      class="text-error"
                    ></v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-menu>
          </div>
        </div>
      </v-app-bar>

      <!-- Premium Navigation Drawer -->
      <v-navigation-drawer
        v-model="drawer"
        :rail="rail"
        permanent
        class="navigation-drawer"
        width="280"
      >
        <div class="drawer-gradient"></div>
        
        <!-- Drawer Header -->
        <div class="drawer-header pa-4">
          <div v-if="!rail" class="d-flex align-center justify-space-between">
            <div class="d-flex align-center">
              <div class="nav-logo-wrapper">
                <v-icon color="white" size="28">mdi-office-building</v-icon>
              </div>
              <div class="ml-3">
                <div class="text-h6 font-weight-bold text-white">Workspace</div>
                <div class="text-caption text-white opacity-70">Team Dashboard</div>
              </div>
            </div>
          </div>
          <v-btn 
            v-else
            icon 
            size="small" 
            variant="text"
            color="white"
            @click="rail = false"
            class="mx-auto"
          >
            <v-icon>mdi-menu</v-icon>
          </v-btn>
          
          <v-btn 
            v-if="!rail"
            icon 
            size="small" 
            variant="text"
            color="white"
            @click="rail = true"
            class="collapse-btn"
          >
            <v-icon>mdi-chevron-left</v-icon>
          </v-btn>
        </div>

        <v-divider class="border-opacity-25" color="white"></v-divider>

        <!-- Navigation Menu -->
        <v-list class="nav-list pa-3" nav>
          <v-list-item
            v-for="item in menuItems"
            :key="item.route"
            :to="item.route"
            :active="route.path === item.route"
            class="nav-item mb-2"
            rounded="xl"
            :style="{ background: getItemGradient(item) }"
          >
            <template v-slot:prepend>
              <div class="nav-icon-wrapper" :style="{ background: route.path === item.route ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.15)' }">
                <v-icon 
                  :color="route.path === item.route ? 'white' : 'white'"
                  size="22"
                >
                  {{ item.icon }}
                </v-icon>
              </div>
            </template>
            
            <v-list-item-title 
              class="font-weight-medium"
              :class="route.path === item.route ? 'text-white' : 'text-white'"
            >
              {{ item.title }}
              <v-chip 
                v-if="!rail && item.shortcut" 
                size="x-small" 
                variant="tonal" 
                color="white"
                class="ml-2"
                label
              >
                {{ item.shortcut }}
              </v-chip>
            </v-list-item-title>
            
            <v-list-item-subtitle 
              v-if="!rail"
              :class="route.path === item.route ? 'text-white opacity-90' : 'text-white opacity-70'"
            >
              {{ item.description }}
            </v-list-item-subtitle>
            
            <template v-slot:append v-if="route.path === item.route && !rail">
              <v-icon color="white" size="20">mdi-chevron-right</v-icon>
            </template>
          </v-list-item>
        </v-list>

        <!-- Bottom Section -->
        <template v-slot:append v-if="!rail">
          <div class="pa-4">
            <!-- Help Card -->
            <v-card variant="outlined" class="help-card" rounded="lg">
              <v-card-text class="pa-4 text-center">
                <v-avatar color="white" size="48" class="mb-3">
                  <v-icon color="primary" size="28">mdi-help-circle</v-icon>
                </v-avatar>
                <div class="text-h6 font-weight-bold text-white mb-1">Need Help?</div>
                <div class="text-caption text-white opacity-80 mb-3">Get support from our team</div>
                <v-btn size="small" variant="flat" color="white" block rounded="lg" @click="navigateTo('/help')">
                  <span class="text-primary font-weight-bold">Contact Support</span>
                </v-btn>
              </v-card-text>
            </v-card>
            
            <!-- Shortcut Info -->
            <div class="text-center mt-4">
              <v-chip size="small" variant="outlined" color="white" class="mb-1">
                <v-icon size="small" class="mr-1">mdi-keyboard</v-icon>
                Ctrl+K to search
              </v-chip>
            </div>
          </div>
        </template>
      </v-navigation-drawer>
    </template>

    <!-- Main Content -->
    <v-main class="main-content">
      <router-view />
    </v-main>
  </v-app>
</template>

<style scoped>
/* App Bar Styles */
.app-bar {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08) !important;
}

.glass-effect {
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1) !important;
}

.brand-section {
  position: relative;
}

.logo-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(21, 101, 192, 0.4);
}

.logo-icon {
  color: white;
}

.brand-text {
  background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.search-wrapper {
  max-width: 500px;
  width: 100%;
}

.search-field {
  border-radius: 16px !important;
  overflow: hidden;
}

.search-field :deep(.v-field) {
  border-radius: 16px;
  box-shadow: none !important;
}

.search-shortcut {
  background: rgba(0, 0, 0, 0.05);
  font-size: 10px;
  font-weight: 600;
  padding: 0 6px;
  height: 20px;
}

.action-btn {
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.user-btn {
  background: rgba(0, 0, 0, 0.02) !important;
  border: 1px solid rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.user-btn:hover {
  background: rgba(0, 0, 0, 0.04) !important;
  transform: translateY(-1px);
}

.avatar-gradient {
  background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%) !important;
  box-shadow: 0 4px 12px rgba(21, 101, 192, 0.3);
}

.user-menu-card {
  border-radius: 16px !important;
  overflow: hidden;
}

.notifications-card {
  border-radius: 16px !important;
  max-height: 500px;
  overflow-y: auto;
}

/* Navigation Drawer Styles */
.navigation-drawer {
  background: linear-gradient(180deg, #1a237e 0%, #0d47a1 100%) !important;
  border-right: none !important;
  position: relative;
  overflow: hidden;
}

.drawer-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 20%, rgba(21, 101, 192, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(13, 71, 161, 0.3) 0%, transparent 50%);
  pointer-events: none;
}

.drawer-header {
  position: relative;
  z-index: 1;
}

.nav-logo-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.collapse-btn {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
}

.nav-list {
  position: relative;
  z-index: 1;
}

.nav-item {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.nav-item:hover {
  transform: translateX(4px);
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.25);
}

.nav-item.v-list-item--active {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.3);
}

.nav-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

/* Help Card */
.help-card {
  transition: all 0.3s ease;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(10px);
}

.help-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.08) !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
}

/* Main Content */
.main-content {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  min-height: 100vh;
}

/* Rail Mode Adjustments */
:deep(.v-navigation-drawer--rail) {
  .nav-item {
    justify-content: center;
  }
  
  .nav-icon-wrapper {
    margin: 0;
  }
}

/* Responsive */
@media (max-width: 960px) {
  .search-wrapper {
    max-width: 300px;
  }
}

@media (max-width: 600px) {
  .app-bar {
    height: 64px !important;
  }
  
  .logo-wrapper {
    width: 40px;
    height: 40px;
  }
  
  .brand-text {
    display: none;
  }
}

/* Scrollbar Styling */
:deep(.v-navigation-drawer__content)::-webkit-scrollbar {
  width: 6px;
}

:deep(.v-navigation-drawer__content)::-webkit-scrollbar-track {
  background: transparent;
}

:deep(.v-navigation-drawer__content)::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

:deep(.v-navigation-drawer__content)::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Dark mode support */
[data-theme="dark"] {
  .app-bar {
    background: rgba(18, 18, 18, 0.95) !important;
    border-bottom-color: rgba(255, 255, 255, 0.08) !important;
  }
  
  .main-content {
    background: linear-gradient(135deg, #121212 0%, #1e1e1e 100%);
  }
  
  .user-btn {
    background: rgba(255, 255, 255, 0.05) !important;
    border-color: rgba(255, 255, 255, 0.12);
  }
  
  .search-field :deep(.v-field) {
    background: rgba(255, 255, 255, 0.05);
  }
}
</style>

<!-- Add helper function for time formatting -->
<script>
function formatTimeAgo(dateString) {
  if (!dateString) return 'Recently'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
</script>
