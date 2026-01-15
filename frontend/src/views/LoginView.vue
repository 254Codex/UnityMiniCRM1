<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const username = ref('demo') // Demo username pre-filled
const password = ref('demo123') // Demo password pre-filled
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

// Check if already logged in
onMounted(() => {
  const token = localStorage.getItem('token')
  if (token) {
    router.push('/')
  }
  
  // Check for error query parameter
  if (route.query.error === 'session_expired') {
    error.value = 'Your session has expired. Please log in again.'
  }
})

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = 'Please enter both username and password'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await api.auth.login({
      username: username.value,
      password: password.value
    })
    
    // Handle different response formats
    const authData = response.data || response
    
    if (authData.token) {
      // Save auth data
      localStorage.setItem('token', authData.token)
      localStorage.setItem('user', JSON.stringify(authData.user))
      
      // Set token expiry (if provided)
      if (authData.expires) {
        localStorage.setItem('token_expiry', authData.expires)
      }
      
      // Check if there's a redirect URL
      const redirect = route.query.redirect || '/'
      router.push(redirect)
    } else {
      throw new Error('No token received from server')
    }
    
  } catch (err) {
    console.error('Login error:', err)
    
    // Handle different error formats
    if (err.response) {
      // Django REST framework error format
      if (err.response.data.detail) {
        error.value = err.response.data.detail
      } 
      // Custom error format
      else if (err.response.data.error) {
        error.value = err.response.data.error
      }
      // Non-field errors
      else if (err.response.data.non_field_errors) {
        error.value = err.response.data.non_field_errors[0]
      }
      // Validation errors
      else if (err.response.data.username || err.response.data.password) {
        error.value = 'Invalid username or password'
      }
      else {
        error.value = 'Login failed. Please try again.'
      }
    } else if (err.request) {
      error.value = 'Cannot connect to server. Please check your connection.'
    } else if (err.message) {
      error.value = err.message
    } else {
      error.value = 'An unexpected error occurred.'
    }
    
    // Clear password on error for security
    password.value = ''
  } finally {
    loading.value = false
  }
}

const handleDemoLogin = () => {
  username.value = 'demo'
  password.value = 'demo123'
  handleLogin()
}

// Handle Enter key press
const handleKeyPress = (event) => {
  if (event.key === 'Enter' && !loading.value) {
    handleLogin()
  }
}
</script>

<template>
  <v-container fluid class="fill-height login-container">
    <v-row align="center" justify="center" class="h-100">
      <v-col cols="12" sm="8" md="5" lg="4" xl="3">
        <!-- Login Card -->
        <v-card elevation="12" rounded="xl" class="pa-6 login-card">
          <!-- Logo Section -->
          <div class="text-center mb-6">
            <div class="logo-container mb-4">
              <v-icon size="72" color="primary" class="logo-icon">mdi-handshake</v-icon>
            </div>
            <h1 class="text-h3 font-weight-bold text-primary mb-2">Mini CRM</h1>
            <p class="text-subtitle-1 text-grey-darken-1">Sign in to your account</p>
          </div>

          <!-- Login Form -->
          <v-form @submit.prevent="handleLogin" @keyup.enter="handleKeyPress">
            <!-- Username Field -->
            <v-text-field
              v-model="username"
              label="Username"
              prepend-inner-icon="mdi-account"
              variant="outlined"
              color="primary"
              class="mb-4"
              :disabled="loading"
              :error-messages="error && error.includes('username') ? error : ''"
              autocomplete="username"
              required
            ></v-text-field>

            <!-- Password Field -->
            <v-text-field
              v-model="password"
              :label="showPassword ? 'Password' : 'Password'"
              :prepend-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
              @click:prepend-inner="showPassword = !showPassword"
              :type="showPassword ? 'text' : 'password'"
              variant="outlined"
              color="primary"
              class="mb-4"
              :disabled="loading"
              :error-messages="error && error.includes('password') ? error : ''"
              autocomplete="current-password"
              required
            ></v-text-field>

            <!-- Error Message -->
            <v-alert
              v-if="error && !error.includes('username') && !error.includes('password')"
              type="error"
              variant="tonal"
              density="comfortable"
              class="mb-4"
              closable
              @click:close="error = ''"
              :icon="false"
            >
              <div class="d-flex align-center">
                <v-icon size="small" class="mr-2">mdi-alert-circle</v-icon>
                <span>{{ error }}</span>
              </div>
            </v-alert>

            <!-- Login Button -->
            <v-btn
              type="submit"
              color="primary"
              size="large"
              block
              :loading="loading"
              :disabled="loading || !username || !password"
              class="mb-4 login-button"
              elevation="2"
            >
              <template v-slot:loader>
                <v-progress-circular indeterminate size="24" color="white"></v-progress-circular>
              </template>
              <v-icon class="mr-2">mdi-login</v-icon>
              Sign In
            </v-btn>

            <!-- Demo Login Button -->
            <v-btn
              color="secondary"
              size="large"
              variant="outlined"
              block
              @click="handleDemoLogin"
              :loading="loading && username === 'demo'"
              class="mb-4 demo-button"
            >
              <v-icon class="mr-2">mdi-account-circle</v-icon>
              Use Demo Account
            </v-btn>

            <!-- Divider -->
            <div class="divider-container my-4">
              <v-divider></v-divider>
              <span class="mx-3 text-caption text-grey-darken-2">or</span>
              <v-divider></v-divider>
            </div>

            <!-- Help Text -->
            <v-alert type="info" variant="tonal" density="compact" class="mb-0">
              <template v-slot:prepend>
                <v-icon color="info">mdi-information</v-icon>
              </template>
              <div class="text-caption">
                <strong>Demo Account Available</strong><br>
                Username: <code>demo</code><br>
                Password: <code>demo123</code>
              </div>
            </v-alert>

            <!-- Version Info -->
            <div class="text-center mt-6 pt-4 border-t">
              <p class="text-caption text-grey-darken-1">
                <v-icon size="small" class="mr-1">mdi-information-outline</v-icon>
                Mini CRM v1.0.0
              </p>
            </div>
          </v-form>
        </v-card>

        <!-- Footer Links -->
        <div class="text-center mt-4">
          <v-btn 
            size="small" 
            variant="text" 
            color="grey-darken-1"
            href="https://github.com/254Codex/UnityMiniCRM1"
            target="_blank"
            class="mr-2"
          >
            <v-icon size="small" class="mr-1">mdi-github</v-icon>
            GitHub
          </v-btn>
          <v-btn 
            size="small" 
            variant="text" 
            color="grey-darken-1"
            href="#"
            @click.prevent="router.push('/forgot-password')"
          >
            <v-icon size="small" class="mr-1">mdi-help-circle</v-icon>
            Need help?
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.login-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-size: 400% 400%;
  animation: gradient 15s ease infinite;
}

@keyframes gradient {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.login-card {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
}

.logo-container {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.logo-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.5;
  }
}

.logo-icon {
  position: relative;
  z-index: 1;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

.login-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.login-button:disabled {
  opacity: 0.7;
}

.demo-button {
  border: 2px solid;
  border-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%) 1;
  transition: all 0.3s ease;
}

.demo-button:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transform: translateY(-2px);
}

.divider-container {
  display: flex;
  align-items: center;
}

.border-t {
  border-top: 1px solid rgba(0, 0, 0, 0.12);
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .login-card {
    padding: 2rem 1.5rem !important;
  }
  
  .logo-container {
    width: 80px;
    height: 80px;
  }
  
  .logo-icon {
    font-size: 48px !important;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .login-card {
    background: rgba(30, 30, 30, 0.95);
  }
  
  .text-navy, .text-grey-darken-1 {
    color: rgba(255, 255, 255, 0.87) !important;
  }
  
  .border-t {
    border-top-color: rgba(255, 255, 255, 0.12);
  }
}

/* Accessibility focus styles */
:deep(.v-field) {
  transition: all 0.2s ease;
}

:deep(.v-field--focused) {
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Custom scrollbar for the container */
.login-container {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}

.login-container::-webkit-scrollbar {
  width: 8px;
}

.login-container::-webkit-scrollbar-track {
  background: transparent;
}

.login-container::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.login-container::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}
</style>

<!-- Add this for PWA/Offline support -->
<script>
// Service worker registration for PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(console.error)
  })
}
</script>
