<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const stats = ref(null)
const loading = ref(true)
const upcomingTasks = ref([])
const recentCompanies = ref([])
const recentContacts = ref([])
const dealPipeline = ref([])
const monthlyTrend = ref([])

onMounted(async () => {
  await loadDashboardData()
})

const loadDashboardData = async () => {
  loading.value = true
  try {
    // Load all dashboard data in parallel
    const [dashboardStats, tasksData, pipelineData, forecastData] = await Promise.all([
      api.dashboard.getStats(),
      api.tasks.getUpcoming(),
      api.deals.getPipeline(),
      api.deals.getForecast()
    ])

    stats.value = dashboardStats.data
    upcomingTasks.value = tasksData.data
    dealPipeline.value = pipelineData.data
    
    // Load recent data if available in stats
    if (dashboardStats.data.recent_companies) {
      recentCompanies.value = dashboardStats.data.recent_companies
    }
    
    if (dashboardStats.data.recent_contacts) {
      recentContacts.value = dashboardStats.data.recent_contacts
    }
    
    if (dashboardStats.data.monthly_trend) {
      monthlyTrend.value = dashboardStats.data.monthly_trend
    }
    
    if (dashboardStats.data.user_stats) {
      // Handle user-specific stats if available
    }

  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  } finally {
    loading.value = false
  }
}

const formatCurrency = (value) => {
  if (!value) return '$0'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

const formatDate = (dateString) => {
  if (!dateString) return 'No date'
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(date)
}

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return 'No date'
  const date = new Date(dateTimeString)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

// Enhanced stage colors for new stages
const getStageColor = (stage) => {
  const colors = {
    'lead': 'blue-grey',
    'qualified': 'blue',
    'proposal': 'purple',
    'negotiation': 'orange',
    'closed_won': 'green',
    'closed_lost': 'red',
    'on_hold': 'grey'
  }
  return colors[stage] || 'grey'
}

const getStageLabel = (stage) => {
  const labels = {
    'lead': 'Lead',
    'qualified': 'Qualified',
    'proposal': 'Proposal',
    'negotiation': 'Negotiation',
    'closed_won': 'Won',
    'closed_lost': 'Lost',
    'on_hold': 'On Hold'
  }
  return labels[stage] || stage
}

// Enhanced priority colors
const getPriorityColor = (priority) => {
  const colors = {
    'low': 'blue',
    'medium': 'orange',
    'high': 'red',
    'urgent': 'deep-orange'
  }
  return colors[priority] || 'grey'
}

// Enhanced status colors
const getStatusColor = (status) => {
  const colors = {
    'pending': 'orange',
    'in_progress': 'blue',
    'completed': 'green',
    'cancelled': 'red',
    'deferred': 'grey'
  }
  return colors[status] || 'grey'
}

const getStatusLabel = (status) => {
  const labels = {
    'pending': 'Pending',
    'in_progress': 'In Progress',
    'completed': 'Completed',
    'cancelled': 'Cancelled',
    'deferred': 'Deferred'
  }
  return labels[status] || status.replace('_', ' ')
}

const navigateTo = (path) => {
  router.push(path)
}

const refreshDashboard = async () => {
  loading.value = true
  await loadDashboardData()
}
</script>

<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-6 flex-wrap gap-3">
          <div>
            <h1 class="text-h3 font-weight-bold text-navy mb-2">Dashboard</h1>
            <p class="text-h6 text-grey-darken-1">Welcome back! Here's what's happening today.</p>
          </div>
          <v-btn
            variant="tonal"
            color="primary"
            prepend-icon="mdi-refresh"
            @click="refreshDashboard"
            :loading="loading"
          >
            Refresh
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <v-row v-if="loading">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      </v-col>
    </v-row>

    <template v-else-if="stats">
      <!-- Main Stats Cards -->
      <v-row class="mb-4">
        <!-- Total Contacts -->
        <v-col cols="12" sm="6" lg="3">
          <v-card
            elevation="3"
            class="stat-card pa-4 cursor-pointer"
            hover
            @click="navigateTo('/contacts')"
          >
            <div class="d-flex align-center justify-space-between">
              <div class="flex-grow-1">
                <p class="text-overline text-grey-darken-1 mb-1">Total Contacts</p>
                <h2 class="text-h3 font-weight-bold text-navy mb-1">{{ stats.total_contacts }}</h2>
                <p class="text-caption text-grey">
                  <v-icon size="small" color="primary" class="mr-1">mdi-account-group</v-icon>
                  View all contacts
                </p>
              </div>
              <v-avatar color="blue lighten-5" size="64">
                <v-icon size="32" color="blue">mdi-account-multiple</v-icon>
              </v-avatar>
            </div>
          </v-card>
        </v-col>

        <!-- Total Companies -->
        <v-col cols="12" sm="6" lg="3">
          <v-card
            elevation="3"
            class="stat-card pa-4 cursor-pointer"
            hover
            @click="navigateTo('/companies')"
          >
            <div class="d-flex align-center justify-space-between">
              <div class="flex-grow-1">
                <p class="text-overline text-grey-darken-1 mb-1">Total Companies</p>
                <h2 class="text-h3 font-weight-bold text-navy mb-1">{{ stats.total_companies }}</h2>
                <p class="text-caption text-grey">
                  <v-icon size="small" color="primary" class="mr-1">mdi-domain</v-icon>
                  View all companies
                </p>
              </div>
              <v-avatar color="purple lighten-5" size="64">
                <v-icon size="32" color="purple">mdi-office-building</v-icon>
              </v-avatar>
            </div>
          </v-card>
        </v-col>

        <!-- Active Deals -->
        <v-col cols="12" sm="6" lg="3">
          <v-card
            elevation="3"
            class="stat-card pa-4 cursor-pointer"
            hover
            @click="navigateTo('/deals')"
          >
            <div class="d-flex align-center justify-space-between">
              <div class="flex-grow-1">
                <p class="text-overline text-grey-darken-1 mb-1">Active Deals</p>
                <h2 class="text-h3 font-weight-bold text-navy mb-1">{{ stats.total_deals }}</h2>
                <p class="text-caption text-success font-weight-medium">
                  Pipeline Value: {{ formatCurrency(stats.active_deals_value) }}
                </p>
              </div>
              <v-avatar color="orange lighten-5" size="64">
                <v-icon size="32" color="orange">mdi-handshake</v-icon>
              </v-avatar>
            </div>
          </v-card>
        </v-col>

        <!-- Weighted Pipeline -->
        <v-col cols="12" sm="6" lg="3">
          <v-card
            elevation="3"
            class="stat-card pa-4 cursor-pointer"
            hover
            @click="navigateTo('/deals')"
          >
            <div class="d-flex align-center justify-space-between">
              <div class="flex-grow-1">
                <p class="text-overline text-grey-darken-1 mb-1">Weighted Pipeline</p>
                <h2 class="text-h4 font-weight-bold text-navy mb-1">{{ formatCurrency(stats.weighted_deals_value) }}</h2>
                <p class="text-caption text-grey">
                  Based on probabilities
                </p>
              </div>
              <v-avatar color="green lighten-5" size="64">
                <v-icon size="32" color="green">mdi-chart-line</v-icon>
              </v-avatar>
            </div>
          </v-card>
        </v-col>
      </v-row>

      <!-- Secondary Stats Row -->
      <v-row class="mb-4">
        <v-col cols="12" sm="6" md="4" lg="2">
          <v-card class="secondary-stat pa-3" elevation="2">
            <div class="text-center">
              <p class="text-caption text-grey mb-1">Pending Tasks</p>
              <h3 class="text-h5 font-weight-bold">{{ stats.pending_tasks }}</h3>
            </div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" lg="2">
          <v-card class="secondary-stat pa-3" elevation="2">
            <div class="text-center">
              <p class="text-caption text-grey mb-1">Overdue Tasks</p>
              <h3 class="text-h5 font-weight-bold text-red">{{ stats.overdue_tasks }}</h3>
            </div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" lg="2">
          <v-card class="secondary-stat pa-3" elevation="2" @click="navigateTo('/tasks')">
            <div class="text-center">
              <p class="text-caption text-grey mb-1">My Tasks</p>
              <h3 class="text-h5 font-weight-bold">{{ stats.user_stats?.assigned_tasks || 0 }}</h3>
            </div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" lg="2">
          <v-card class="secondary-stat pa-3" elevation="2" @click="navigateTo('/deals')">
            <div class="text-center">
              <p class="text-caption text-grey mb-1">My Deals</p>
              <h3 class="text-h5 font-weight-bold">{{ stats.user_stats?.assigned_deals || 0 }}</h3>
            </div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" lg="2">
          <v-card class="secondary-stat pa-3" elevation="2">
            <div class="text-center">
              <p class="text-caption text-grey mb-1">My Activity</p>
              <h3 class="text-h5 font-weight-bold">{{ stats.user_stats?.recent_activity || 0 }}</h3>
            </div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="4" lg="2">
          <v-card class="secondary-stat pa-3" elevation="2">
            <div class="text-center">
              <p class="text-caption text-grey mb-1">Total Tasks</p>
              <h3 class="text-h5 font-weight-bold">{{ stats.total_tasks }}</h3>
            </div>
          </v-card>
        </v-col>
      </v-row>

      <!-- Main Content Row -->
      <v-row>
        <!-- Left Column (2/3 width) -->
        <v-col cols="12" lg="8">
          <!-- Sales Pipeline -->
          <v-card elevation="3" class="mb-4">
            <v-card-title class="pa-4 bg-grey-lighten-4">
              <div class="d-flex align-center justify-space-between w-100">
                <div class="d-flex align-center">
                  <v-icon class="mr-2" color="primary">mdi-chart-bar</v-icon>
                  <span class="text-h6 font-weight-bold">Sales Pipeline</span>
                </div>
                <v-btn
                  size="small"
                  variant="text"
                  color="primary"
                  @click="navigateTo('/deals')"
                >
                  View All
                  <v-icon size="small" class="ml-1">mdi-arrow-right</v-icon>
                </v-btn>
              </div>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pa-4">
              <v-row v-if="stats.deal_pipeline">
                <v-col
                  v-for="(count, stage) in stats.deal_pipeline"
                  :key="stage"
                  cols="6"
                  sm="4"
                  md="3"
                  class="mb-3"
                >
                  <div class="pipeline-stage pa-3 rounded border">
                    <div class="d-flex align-center justify-space-between mb-2">
                      <v-chip
                        :color="getStageColor(stage)"
                        size="small"
                        variant="flat"
                        class="font-weight-bold"
                      >
                        {{ getStageLabel(stage) }}
                      </v-chip>
                      <span class="text-h5 font-weight-bold">{{ count }}</span>
                    </div>
                    <v-progress-linear
                      :model-value="stats.total_deals > 0 ? (count / stats.total_deals) * 100 : 0"
                      :color="getStageColor(stage)"
                      height="6"
                      rounded
                    ></v-progress-linear>
                  </div>
                </v-col>
              </v-row>
              <v-row v-else-if="dealPipeline.length > 0">
                <v-col
                  v-for="stage in dealPipeline"
                  :key="stage.stage"
                  cols="6"
                  sm="4"
                  md="3"
                  class="mb-3"
                >
                  <div class="pipeline-stage pa-3 rounded border">
                    <div class="d-flex align-center justify-space-between mb-2">
                      <v-chip
                        :color="getStageColor(stage.stage)"
                        size="small"
                        variant="flat"
                        class="font-weight-bold"
                      >
                        {{ getStageLabel(stage.stage) }}
                      </v-chip>
                      <span class="text-h5 font-weight-bold">{{ stage.count }}</span>
                    </div>
                    <div class="text-caption text-grey mb-1">
                      Value: {{ formatCurrency(stage.total_amount) }}
                    </div>
                    <v-progress-linear
                      :model-value="stage.count > 0 ? Math.min(100, stage.count * 10) : 0"
                      :color="getStageColor(stage.stage)"
                      height="6"
                      rounded
                    ></v-progress-linear>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Tasks Overview -->
          <v-card elevation="3">
            <v-card-title class="pa-4 bg-grey-lighten-4">
              <div class="d-flex align-center justify-space-between w-100">
                <div class="d-flex align-center">
                  <v-icon class="mr-2" color="primary">mdi-clipboard-check</v-icon>
                  <span class="text-h6 font-weight-bold">Upcoming Tasks</span>
                </div>
                <v-btn
                  size="small"
                  variant="text"
                  color="primary"
                  @click="navigateTo('/tasks')"
                >
                  View All
                  <v-icon size="small" class="ml-1">mdi-arrow-right</v-icon>
                </v-btn>
              </div>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pa-0">
              <v-list v-if="upcomingTasks.length > 0" lines="two">
                <v-list-item
                  v-for="(task, index) in upcomingTasks"
                  :key="task.id"
                  class="px-4 py-3"
                  :class="{ 'bg-grey-lighten-5': index % 2 === 0 }"
                  @click="navigateTo(`/tasks/${task.id}`)"
                >
                  <template v-slot:prepend>
                    <v-icon
                      :color="getStatusColor(task.status)"
                      class="mr-3"
                    >
                      {{ task.task_type === 'call' ? 'mdi-phone' : 
                         task.task_type === 'email' ? 'mdi-email' : 
                         task.task_type === 'meeting' ? 'mdi-calendar' : 
                         'mdi-checkbox-marked-circle' }}
                    </v-icon>
                  </template>

                  <v-list-item-title class="font-weight-medium mb-1">
                    {{ task.title }}
                    <v-chip v-if="task.related_entity" size="x-small" class="ml-2">
                      {{ task.contact ? 'Contact' : task.deal ? 'Deal' : 'Company' }}
                    </v-chip>
                  </v-list-item-title>
                  
                  <v-list-item-subtitle class="text-caption">
                    <v-icon size="x-small" class="mr-1">mdi-calendar-clock</v-icon>
                    {{ formatDateTime(task.due_date) }}
                    <template v-if="task.estimated_hours">
                      • {{ task.estimated_hours }}h
                    </template>
                  </v-list-item-subtitle>

                  <template v-slot:append>
                    <div class="d-flex flex-column align-end gap-1">
                      <v-chip
                        :color="getPriorityColor(task.priority)"
                        size="x-small"
                        variant="flat"
                        class="text-capitalize"
                      >
                        {{ task.priority }}
                      </v-chip>
                      <v-chip
                        :color="getStatusColor(task.status)"
                        size="x-small"
                        variant="outlined"
                        class="text-capitalize"
                      >
                        {{ getStatusLabel(task.status) }}
                      </v-chip>
                    </div>
                  </template>
                </v-list-item>
              </v-list>
              <div v-else class="pa-8 text-center text-grey">
                <v-icon size="48" color="grey-lighten-1" class="mb-2">mdi-check-all</v-icon>
                <p>No upcoming tasks</p>
                <v-btn size="small" color="primary" variant="text" @click="navigateTo('/tasks')">
                  Create your first task
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Right Column (1/3 width) -->
        <v-col cols="12" lg="4">
          <!-- Quick Actions -->
          <v-card elevation="3" class="mb-4">
            <v-card-title class="pa-4 bg-grey-lighten-4">
              <v-icon class="mr-2" color="primary">mdi-lightning-bolt</v-icon>
              <span class="text-h6 font-weight-bold">Quick Actions</span>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pa-3">
              <v-list density="compact">
                <v-list-item
                  @click="navigateTo('/contacts/create')"
                  class="rounded mb-2 cursor-pointer"
                  prepend-icon="mdi-account-plus"
                  title="Add New Contact"
                  subtitle="Create a new contact"
                ></v-list-item>
                <v-list-item
                  @click="navigateTo('/companies/create')"
                  class="rounded mb-2 cursor-pointer"
                  prepend-icon="mdi-office-building-plus"
                  title="Add New Company"
                  subtitle="Create a new company"
                ></v-list-item>
                <v-list-item
                  @click="navigateTo('/deals/create')"
                  class="rounded mb-2 cursor-pointer"
                  prepend-icon="mdi-handshake-outline"
                  title="Create New Deal"
                  subtitle="Start a new deal"
                ></v-list-item>
                <v-list-item
                  @click="navigateTo('/tasks/create')"
                  class="rounded cursor-pointer"
                  prepend-icon="mdi-plus-circle"
                  title="Add New Task"
                  subtitle="Create a new task"
                ></v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

          <!-- Recent Companies -->
          <v-card elevation="3" class="mb-4" v-if="recentCompanies.length > 0">
            <v-card-title class="pa-4 bg-grey-lighten-4">
              <div class="d-flex align-center justify-space-between w-100">
                <div class="d-flex align-center">
                  <v-icon class="mr-2" color="primary">mdi-domain</v-icon>
                  <span class="text-h6 font-weight-bold">Recent Companies</span>
                </div>
                <v-btn
                  size="small"
                  variant="text"
                  color="primary"
                  @click="navigateTo('/companies')"
                >
                  View All
                </v-btn>
              </div>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pa-0">
              <v-list lines="two">
                <v-list-item
                  v-for="company in recentCompanies.slice(0, 4)"
                  :key="company.id"
                  @click="navigateTo(`/companies/${company.id}`)"
                  class="px-3 py-2"
                >
                  <template v-slot:prepend>
                    <v-avatar size="40" color="primary" class="mr-3">
                      <span class="text-white font-weight-bold">
                        {{ company.name.substring(0, 2).toUpperCase() }}
                      </span>
                    </v-avatar>
                  </template>
                  <v-list-item-title class="font-weight-medium text-truncate">
                    {{ company.name }}
                  </v-list-item-title>
                  <v-list-item-subtitle class="text-caption">
                    {{ company.industry_display || 'No industry' }}
                    <template v-if="company.city">
                      • {{ company.city }}
                    </template>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

          <!-- Activity Summary -->
          <v-card elevation="3">
            <v-card-title class="pa-4 bg-grey-lighten-4">
              <v-icon class="mr-2" color="primary">mdi-chart-pie</v-icon>
              <span class="text-h6 font-weight-bold">Performance</span>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pa-4">
              <!-- Win Rate -->
              <div class="mb-4">
                <div class="d-flex justify-space-between align-center mb-2">
                  <span class="text-body-2 text-grey-darken-2">Pipeline Win Rate</span>
                  <span class="text-h6 font-weight-bold text-green">
                    {{ stats.total_deals > 0 ? 
                       Math.round((stats.deal_pipeline?.closed_won || 0) / stats.total_deals * 100) : 0 }}%
                  </span>
                </div>
                <v-progress-linear
                  :model-value="stats.total_deals > 0 ? 
                    (stats.deal_pipeline?.closed_won || 0) / stats.total_deals * 100 : 0"
                  color="green"
                  height="8"
                  rounded
                ></v-progress-linear>
              </div>

              <!-- Task Completion -->
              <div class="mb-4">
                <div class="d-flex justify-space-between align-center mb-2">
                  <span class="text-body-2 text-grey-darken-2">Task Completion</span>
                  <span class="text-h6 font-weight-bold text-blue">
                    {{ stats.total_tasks > 0 ? 
                       Math.round((stats.total_tasks - stats.pending_tasks - stats.overdue_tasks) / stats.total_tasks * 100) : 0 }}%
                  </span>
                </div>
                <v-progress-linear
                  :model-value="stats.total_tasks > 0 ? 
                    (stats.total_tasks - stats.pending_tasks - stats.overdue_tasks) / stats.total_tasks * 100 : 0"
                  color="blue"
                  height="8"
                  rounded
                ></v-progress-linear>
              </div>

              <!-- Activity Level -->
              <div>
                <div class="d-flex justify-space-between align-center mb-2">
                  <span class="text-body-2 text-grey-darken-2">Activity Level</span>
                  <span class="text-h6 font-weight-bold text-purple">
                    {{ stats.user_stats?.recent_activity || 0 }}
                  </span>
                </div>
                <div class="text-caption text-grey">
                  Recent interactions
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>

<style scoped>
.stat-card {
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.stat-card:hover {
  transform: translateY(-4px);
  border-left-color: rgb(var(--v-theme-primary));
}

.secondary-stat {
  transition: all 0.2s ease;
  text-align: center;
}

.secondary-stat:hover {
  background-color: rgba(0, 0, 0, 0.02);
  transform: translateY(-2px);
}

.cursor-pointer {
  cursor: pointer;
}

.pipeline-stage {
  transition: all 0.2s ease;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.pipeline-stage:hover {
  background-color: rgba(0, 0, 0, 0.02);
  transform: scale(1.02);
  border-color: rgba(0, 0, 0, 0.2);
}

.text-navy {
  color: #1a237e;
}
</style>
