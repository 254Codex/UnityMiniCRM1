<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const tasks = ref([])
const deals = ref([])
const contacts = ref([])
const users = ref([])
const loading = ref(true)
const dialog = ref(false)
const viewMode = ref('card')
const search = ref('')
const statusFilter = ref('all')
const priorityFilter = ref('all')
const editedIndex = ref(-1)
const editedItem = ref({
  title: '',
  description: '',
  task_type: 'other',
  status: 'pending',
  priority: 'medium',
  due_date: '',
  estimated_hours: null,
  deal: null,
  contact: null,
  company: null,
  assigned_to: null,
  tags: []
})

const defaultItem = {
  title: '',
  description: '',
  task_type: 'other',
  status: 'pending',
  priority: 'medium',
  due_date: '',
  estimated_hours: null,
  deal: null,
  contact: null,
  company: null,
  assigned_to: null,
  tags: []
}

// Use constants from your API
const taskTypeOptions = api.constants.TASK_TYPE_CHOICES
const statusOptions = api.constants.TASK_STATUS_CHOICES
const priorityOptions = api.constants.TASK_PRIORITY_CHOICES

const headers = [
  { title: 'Task', key: 'title', sortable: true },
  { title: 'Type', key: 'task_type', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Priority', key: 'priority', sortable: true },
  { title: 'Due Date', key: 'due_date', sortable: true },
  { title: 'Estimated Hours', key: 'estimated_hours', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
]

// Computed properties
const filteredTasks = computed(() => {
  let filtered = tasks.value

  if (search.value) {
    const searchLower = search.value.toLowerCase()
    filtered = filtered.filter(task =>
      task.title?.toLowerCase().includes(searchLower) ||
      task.description?.toLowerCase().includes(searchLower) ||
      task.tags?.toLowerCase().includes(searchLower)
    )
  }

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(task => task.status === statusFilter.value)
  }

  if (priorityFilter.value !== 'all') {
    filtered = filtered.filter(task => task.priority === priorityFilter.value)
  }

  return filtered
})

const pendingTasks = computed(() => {
  return tasks.value.filter(task => task.status === 'pending' && !isOverdue(task.due_date, task.status)).length
})

const overdueTasks = computed(() => {
  return tasks.value.filter(task => task.status !== 'completed' && isOverdue(task.due_date, task.status)).length
})

const completedTasks = computed(() => {
  return tasks.value.filter(task => task.status === 'completed').length
})

// Lifecycle
onMounted(async () => {
  await Promise.all([loadTasks(), loadDeals(), loadContacts(), loadUsers()])
})

// Data loading methods
const loadTasks = async () => {
  loading.value = true
  try {
    const response = await api.tasks.getAll()
    tasks.value = response.data.map(task => ({
      ...task,
      // Ensure proper field names
      deal_title: task.deal?.title || '',
      contact_name: task.contact ? `${task.contact.first_name} ${task.contact.last_name}` : '',
      assigned_to_name: task.assigned_to?.username || ''
    }))
  } catch (error) {
    console.error('Failed to load tasks:', error)
  } finally {
    loading.value = false
  }
}

const loadDeals = async () => {
  try {
    const response = await api.deals.getAll({ limit: 100 })
    deals.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to load deals:', error)
  }
}

const loadContacts = async () => {
  try {
    const response = await api.contacts.getAll({ limit: 100 })
    contacts.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to load contacts:', error)
  }
}

const loadUsers = async () => {
  try {
    const response = await api.users.getAll()
    users.value = response.data
  } catch (error) {
    console.error('Failed to load users:', error)
  }
}

// Utility functions
const getTaskTypeColor = (taskType) => {
  const colors = {
    call: 'blue',
    email: 'green',
    meeting: 'purple',
    follow_up: 'orange',
    document: 'red',
    other: 'grey'
  }
  return colors[taskType] || 'grey'
}

const getTaskTypeLabel = (taskType) => {
  const option = taskTypeOptions.find(t => t.value === taskType)
  return option ? option.label : taskType.replace('_', ' ')
}

const getTaskTypeIcon = (taskType) => {
  const icons = {
    call: 'mdi-phone',
    email: 'mdi-email',
    meeting: 'mdi-calendar',
    follow_up: 'mdi-calendar-check',
    document: 'mdi-file-document',
    other: 'mdi-checkbox-marked-circle-outline'
  }
  return icons[taskType] || 'mdi-help-circle'
}

const getStatusColor = (status) => {
  const colors = {
    pending: 'orange',
    in_progress: 'blue',
    completed: 'green',
    cancelled: 'red',
    deferred: 'grey'
  }
  return colors[status] || 'grey'
}

const getStatusLabel = (status) => {
  const option = statusOptions.find(s => s.value === status)
  return option ? option.label : status.replace('_', ' ')
}

const getPriorityColor = (priority) => {
  const colors = {
    low: 'blue',
    medium: 'orange',
    high: 'red',
    urgent: 'deep-orange'
  }
  return colors[priority] || 'grey'
}

const getPriorityLabel = (priority) => {
  const option = priorityOptions.find(p => p.value === priority)
  return option ? option.label : priority
}

const formatDate = (date) => {
  if (!date) return 'No date'
  try {
    const dateObj = new Date(date)
    const now = new Date()
    const diffTime = dateObj - now
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    const dateStr = dateObj.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: dateObj.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    })
    
    if (diffDays === 0) return `Today, ${dateStr}`
    if (diffDays === 1) return `Tomorrow, ${dateStr}`
    if (diffDays < 0) return `${Math.abs(diffDays)} days ago`
    if (diffDays <= 7) return `In ${diffDays} days, ${dateStr}`
    
    return dateStr
  } catch {
    return 'Invalid date'
  }
}

const formatTime = (hours) => {
  if (!hours) return 'N/A'
  return `${hours}h`
}

const isOverdue = (dueDate, status) => {
  if (!dueDate || status === 'completed' || status === 'cancelled') return false
  return new Date(dueDate) < new Date()
}

const isDueSoon = (dueDate, status) => {
  if (!dueDate || status === 'completed' || status === 'cancelled') return false
  const due = new Date(dueDate)
  const now = new Date()
  const diffTime = due - now
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays >= 0 && diffDays <= 2
}

// CRUD operations
const editItem = (item) => {
  editedIndex.value = tasks.value.findIndex(t => t.id === item.id)
  editedItem.value = {
    ...item,
    deal: item.deal?.id || item.deal,
    contact: item.contact?.id || item.contact,
    company: item.company?.id || item.company,
    assigned_to: item.assigned_to?.id || item.assigned_to,
    tags: item.tags ? item.tags.split(',') : []
  }
  dialog.value = true
}

const deleteItem = async (item) => {
  if (confirm('Are you sure you want to delete this task?')) {
    try {
      await api.tasks.delete(item.id)
      await loadTasks()
    } catch (error) {
      console.error('Failed to delete task:', error)
      alert('Failed to delete task. Please try again.')
    }
  }
}

const completeItem = async (item) => {
  if (confirm('Mark this task as completed?')) {
    try {
      await api.tasks.complete(item.id, {
        actual_hours: item.estimated_hours || 0,
        completion_notes: 'Completed via dashboard'
      })
      await loadTasks()
    } catch (error) {
      console.error('Failed to complete task:', error)
    }
  }
}

const close = () => {
  dialog.value = false
  setTimeout(() => {
    editedItem.value = { ...defaultItem }
    editedIndex.value = -1
  }, 300)
}

const save = async () => {
  // Validate required fields
  if (!editedItem.value.title?.trim()) {
    alert('Task title is required')
    return
  }

  try {
    // Prepare data for API
    const taskData = {
      title: editedItem.value.title,
      description: editedItem.value.description || '',
      task_type: editedItem.value.task_type,
      status: editedItem.value.status,
      priority: editedItem.value.priority,
      due_date: editedItem.value.due_date || null,
      estimated_hours: editedItem.value.estimated_hours || null,
      deal: editedItem.value.deal,
      contact: editedItem.value.contact,
      company: editedItem.value.company,
      assigned_to: editedItem.value.assigned_to,
      tags: editedItem.value.tags?.join(',') || ''
    }

    if (editedIndex.value > -1) {
      await api.tasks.update(editedItem.value.id, taskData)
    } else {
      await api.tasks.create(taskData)
    }
    
    await loadTasks()
    close()
  } catch (error) {
    console.error('Failed to save task:', error)
    alert('Failed to save task. Please check the form and try again.')
  }
}

const viewTask = (task) => {
  router.push(`/tasks/${task.id}`)
}

const getTaskColor = (index) => {
  const colors = ['primary', 'secondary', 'success', 'info', 'warning', 'purple', 'pink', 'indigo', 'teal', 'orange']
  return colors[index % colors.length]
}

const clearFilters = () => {
  search.value = ''
  statusFilter.value = 'all'
  priorityFilter.value = 'all'
}

// Watch for changes in filters
watch([search, statusFilter, priorityFilter], () => {
  // You could add debouncing here if needed
})

// Handle keyboard shortcuts
const handleKeyPress = (event) => {
  if (event.ctrlKey || event.metaKey) {
    switch(event.key) {
      case 'n':
        event.preventDefault()
        dialog.value = true
        break
      case 'f':
        event.preventDefault()
        const searchInput = document.querySelector('input[type="text"]')
        if (searchInput) searchInput.focus()
        break
    }
  }
}

// Add event listener for keyboard shortcuts
onMounted(() => {
  window.addEventListener('keydown', handleKeyPress)
})

// Cleanup
import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
})
</script>

<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-6 flex-wrap gap-3">
          <div>
            <h1 class="text-h3 font-weight-bold text-navy mb-2">Tasks</h1>
            <p class="text-h6 text-grey-darken-1">Manage your to-do list</p>
            <div class="d-flex align-center gap-4 mt-2">
              <div class="d-flex align-center gap-1">
                <v-icon size="small" color="orange">mdi-clock-outline</v-icon>
                <span class="text-body-2 text-grey-darken-1">Pending:</span>
                <span class="text-h6 font-weight-bold ml-1">{{ pendingTasks }}</span>
              </div>
              <div class="d-flex align-center gap-1">
                <v-icon size="small" color="red">mdi-alert</v-icon>
                <span class="text-body-2 text-grey-darken-1">Overdue:</span>
                <span class="text-h6 font-weight-bold text-red ml-1">{{ overdueTasks }}</span>
              </div>
              <div class="d-flex align-center gap-1">
                <v-icon size="small" color="green">mdi-check-circle</v-icon>
                <span class="text-body-2 text-grey-darken-1">Completed:</span>
                <span class="text-h6 font-weight-bold text-green ml-1">{{ completedTasks }}</span>
              </div>
            </div>
          </div>
          <div class="d-flex gap-2">
            <v-btn
              color="primary"
              size="large"
              prepend-icon="mdi-plus"
              @click="dialog = true"
              elevation="2"
            >
              Add Task
              <v-tooltip activator="parent" location="bottom">Ctrl+N</v-tooltip>
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Search and Filters -->
    <v-row>
      <v-col cols="12">
        <v-card elevation="2" class="mb-4">
          <v-card-text class="pa-4">
            <div class="d-flex align-center gap-3 flex-wrap">
              <v-text-field
                v-model="search"
                prepend-inner-icon="mdi-magnify"
                label="Search tasks..."
                variant="outlined"
                density="compact"
                hide-details
                clearable
                class="flex-grow-1"
                style="max-width: 300px;"
              >
                <template v-slot:append-inner>
                  <v-tooltip location="bottom">Ctrl+F to focus</v-tooltip>
                </template>
              </v-text-field>
              
              <v-select
                v-model="statusFilter"
                :items="[{ title: 'All Statuses', value: 'all' }, ...statusOptions]"
                label="Status"
                variant="outlined"
                density="compact"
                style="max-width: 200px;"
                hide-details
              ></v-select>
              
              <v-select
                v-model="priorityFilter"
                :items="[{ title: 'All Priorities', value: 'all' }, ...priorityOptions]"
                label="Priority"
                variant="outlined"
                density="compact"
                style="max-width: 200px;"
                hide-details
              ></v-select>
              
              <v-btn
                v-if="search || statusFilter !== 'all' || priorityFilter !== 'all'"
                variant="text"
                color="grey"
                size="small"
                prepend-icon="mdi-filter-remove"
                @click="clearFilters"
              >
                Clear Filters
              </v-btn>
              
              <v-spacer></v-spacer>
              
              <v-btn-toggle v-model="viewMode" mandatory variant="outlined" divided density="compact">
                <v-btn value="card" size="small" title="Card View">
                  <v-icon>mdi-view-grid</v-icon>
                </v-btn>
                <v-btn value="table" size="small" title="Table View">
                  <v-icon>mdi-view-list</v-icon>
                </v-btn>
              </v-btn-toggle>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <v-row v-if="loading">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <p class="mt-4 text-body-1 text-grey">Loading tasks...</p>
      </v-col>
    </v-row>

    <!-- Card View -->
    <v-row v-else-if="viewMode === 'card'">
      <v-col 
        v-for="(task, index) in filteredTasks" 
        :key="task.id" 
        cols="12" 
        sm="6" 
        md="4" 
        lg="3"
      >
        <v-card 
          elevation="3" 
          class="task-card h-100 cursor-pointer"
          :class="{ 
            'overdue-card': isOverdue(task.due_date, task.status),
            'due-soon-card': isDueSoon(task.due_date, task.status)
          }"
          hover
          @click="viewTask(task)"
        >
          <v-card-text class="pa-4">
            <div class="d-flex align-center justify-space-between mb-3">
              <div class="d-flex align-center">
                <v-avatar :color="getTaskTypeColor(task.task_type)" size="40" class="mr-3">
                  <v-icon :icon="getTaskTypeIcon(task.task_type)" color="white" size="20"></v-icon>
                </v-avatar>
                <div>
                  <v-chip 
                    :color="getPriorityColor(task.priority)" 
                    size="x-small" 
                    variant="flat" 
                    class="text-capitalize font-weight-bold mb-1"
                  >
                    {{ getPriorityLabel(task.priority) }}
                  </v-chip>
                  <div v-if="isOverdue(task.due_date, task.status)" class="d-flex align-center">
                    <v-icon size="x-small" color="error" class="mr-1">mdi-alert</v-icon>
                    <span class="text-caption font-weight-bold text-error">OVERDUE</span>
                  </div>
                </div>
              </div>
              
              <v-btn
                v-if="task.status !== 'completed'"
                icon
                size="small"
                variant="text"
                color="success"
                @click.stop="completeItem(task)"
                title="Mark as Complete"
              >
                <v-icon size="small">mdi-check</v-icon>
              </v-btn>
            </div>

            <h3 class="text-h6 font-weight-bold mb-2">{{ task.title }}</h3>
            <p v-if="task.description" class="text-caption text-grey-darken-1 mb-3 task-description">
              {{ task.description }}
            </p>

            <v-divider class="my-3"></v-divider>

            <div class="task-details">
              <div class="d-flex align-center justify-space-between mb-2">
                <v-chip 
                  :color="getStatusColor(task.status)" 
                  size="x-small" 
                  variant="flat" 
                  class="text-capitalize font-weight-bold"
                >
                  {{ getStatusLabel(task.status) }}
                </v-chip>
                <span v-if="task.estimated_hours" class="text-caption font-weight-medium">
                  {{ formatTime(task.estimated_hours) }}
                </span>
              </div>

              <div class="d-flex align-center mb-2" v-if="task.deal_title">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-handshake</v-icon>
                <span class="text-caption font-weight-medium text-truncate">{{ task.deal_title }}</span>
              </div>

              <div class="d-flex align-center mb-2" v-if="task.contact_name">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-account</v-icon>
                <span class="text-caption text-truncate">{{ task.contact_name }}</span>
              </div>

              <div class="d-flex align-center justify-space-between">
                <div class="d-flex align-center">
                  <v-icon 
                    size="small" 
                    class="mr-2" 
                    :color="isOverdue(task.due_date, task.status) ? 'error' : 
                           isDueSoon(task.due_date, task.status) ? 'orange' : 'grey-darken-1'"
                  >
                    mdi-calendar
                  </v-icon>
                  <span class="text-caption" 
                    :class="{ 
                      'text-error font-weight-bold': isOverdue(task.due_date, task.status),
                      'text-orange font-weight-medium': isDueSoon(task.due_date, task.status)
                    }"
                  >
                    {{ formatDate(task.due_date) }}
                  </span>
                </div>
                
                <v-chip 
                  v-if="task.tags" 
                  size="x-small" 
                  variant="tonal" 
                  color="grey"
                  class="text-truncate"
                  style="max-width: 100px;"
                >
                  {{ task.tags.split(',')[0] }}
                </v-chip>
              </div>
            </div>
          </v-card-text>
          <v-card-actions class="pa-3 pt-0">
            <v-btn 
              size="small" 
              variant="text" 
              color="primary" 
              prepend-icon="mdi-pencil"
              @click.stop="editItem(task)"
            >
              Edit
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn 
              size="small" 
              variant="text" 
              color="error" 
              icon="mdi-delete"
              @click.stop="deleteItem(task)"
            ></v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <!-- Empty State -->
      <v-col v-if="filteredTasks.length === 0" cols="12">
        <v-card elevation="2" class="pa-12">
          <div class="text-center">
            <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-clipboard-check-outline</v-icon>
            <h3 class="text-h5 mb-2 text-grey-darken-1">No tasks found</h3>
            <p class="text-body-2 text-grey mb-4">
              {{ search || statusFilter !== 'all' || priorityFilter !== 'all' ? 
                'Try adjusting your filters' : 'Get started by adding your first task' }}
            </p>
            <v-btn v-if="!search && statusFilter === 'all' && priorityFilter === 'all'" 
              color="primary" 
              @click="dialog = true" 
              prepend-icon="mdi-plus"
            >
              Add Your First Task
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Table View -->
    <v-row v-else>
      <v-col cols="12">
        <v-card elevation="3">
          <v-data-table 
            :headers="headers" 
            :items="filteredTasks" 
            :loading="loading" 
            items-per-page="15"
            class="elevation-1"
          >
            <template v-slot:item.title="{ item }">
              <div class="d-flex align-center py-2 cursor-pointer" @click="viewTask(item)">
                <v-avatar :color="getTaskTypeColor(item.task_type)" size="36" class="mr-3">
                  <v-icon :icon="getTaskTypeIcon(item.task_type)" color="white" size="18"></v-icon>
                </v-avatar>
                <div>
                  <span class="font-weight-medium d-block">{{ item.title }}</span>
                  <span v-if="item.description" class="text-caption text-grey text-truncate" style="max-width: 300px;">
                    {{ item.description }}
                  </span>
                </div>
              </div>
            </template>
            
            <template v-slot:item.task_type="{ item }">
              <v-chip 
                :color="getTaskTypeColor(item.task_type)" 
                size="x-small" 
                variant="tonal" 
                class="text-capitalize"
              >
                {{ getTaskTypeLabel(item.task_type) }}
              </v-chip>
            </template>
            
            <template v-slot:item.status="{ item }">
              <v-chip 
                :color="getStatusColor(item.status)" 
                size="small" 
                variant="flat" 
                class="text-capitalize font-weight-bold"
              >
                {{ getStatusLabel(item.status) }}
              </v-chip>
            </template>
            
            <template v-slot:item.priority="{ item }">
              <v-chip 
                :color="getPriorityColor(item.priority)" 
                size="small" 
                variant="tonal" 
                class="text-capitalize font-weight-bold"
              >
                {{ getPriorityLabel(item.priority) }}
              </v-chip>
            </template>
            
            <template v-slot:item.due_date="{ item }">
              <div v-if="item.due_date" class="d-flex align-center gap-1">
                <span :class="{ 
                  'text-error font-weight-bold': isOverdue(item.due_date, item.status),
                  'text-orange font-weight-medium': isDueSoon(item.due_date, item.status)
                }">
                  {{ formatDate(item.due_date) }}
                </span>
                <v-chip v-if="isOverdue(item.due_date, item.status)" color="error" size="x-small" variant="flat">
                  Overdue
                </v-chip>
                <v-chip v-else-if="isDueSoon(item.due_date, item.status)" color="orange" size="x-small" variant="tonal">
                  Soon
                </v-chip>
              </div>
              <span v-else class="text-grey">-</span>
            </template>
            
            <template v-slot:item.estimated_hours="{ item }">
              <span v-if="item.estimated_hours" class="font-weight-medium">
                {{ formatTime(item.estimated_hours) }}
              </span>
              <span v-else class="text-grey">-</span>
            </template>
            
            <template v-slot:item.actions="{ item }">
              <v-btn
                v-if="item.status !== 'completed'"
                icon
                size="small"
                variant="text"
                color="success"
                @click.stop="completeItem(item)"
                title="Mark Complete"
              >
                <v-icon size="small">mdi-check</v-icon>
              </v-btn>
              <v-btn
                icon
                size="small"
                variant="text"
                color="primary"
                @click.stop="editItem(item)"
                title="Edit"
              >
                <v-icon size="small">mdi-pencil</v-icon>
              </v-btn>
              <v-btn
                icon
                size="small"
                variant="text"
                color="error"
                @click.stop="deleteItem(item)"
                title="Delete"
              >
                <v-icon size="small">mdi-delete</v-icon>
              </v-btn>
            </template>
            
            <!-- Empty State -->
            <template v-slot:no-data>
              <div class="pa-8 text-center">
                <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-clipboard-check-outline</v-icon>
                <h3 class="text-h5 mb-2 text-grey-darken-1">No tasks found</h3>
                <p class="text-body-2 text-grey mb-4">
                  {{ search || statusFilter !== 'all' || priorityFilter !== 'all' ? 
                    'Try adjusting your filters' : 'Get started by adding your first task' }}
                </p>
                <v-btn v-if="!search && statusFilter === 'all' && priorityFilter === 'all'" 
                  color="primary" 
                  @click="dialog = true" 
                  prepend-icon="mdi-plus"
                >
                  Add Task
                </v-btn>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- Task Dialog -->
    <v-dialog v-model="dialog" max-width="800px" persistent>
      <v-card>
        <v-card-title class="pa-4 bg-grey-lighten-4">
          <div class="d-flex align-center">
            <v-icon class="mr-2" color="primary">
              {{ editedIndex === -1 ? 'mdi-clipboard-plus' : 'mdi-clipboard-edit' }}
            </v-icon>
            <span class="text-h6 font-weight-bold">
              {{ editedIndex === -1 ? 'New Task' : 'Edit Task' }}
            </span>
          </div>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-6">
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="editedItem.title"
                  label="Task Title *"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-text"
                  required
                  :rules="[v => !!v || 'Title is required']"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="editedItem.description"
                  label="Description"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-text-box"
                  rows="3"
                  auto-grow
                ></v-textarea>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.task_type"
                  :items="taskTypeOptions"
                  label="Task Type"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-format-list-bulleted-type"
                ></v-select>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.status"
                  :items="statusOptions"
                  label="Status *"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-chart-timeline-variant"
                  required
                  :rules="[v => !!v || 'Status is required']"
                ></v-select>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.priority"
                  :items="priorityOptions"
                  label="Priority *"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-flag"
                  required
                  :rules="[v => !!v || 'Priority is required']"
                ></v-select>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedItem.estimated_hours"
                  label="Estimated Hours"
                  type="number"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-clock"
                  min="0"
                  step="0.5"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="editedItem.due_date"
                  label="Due Date"
                  type="date"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-calendar"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.deal"
                  :items="deals"
                  item-title="title"
                  item-value="id"
                  label="Related Deal"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-handshake"
                  clearable
                ></v-select>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.contact"
                  :items="contacts"
                  item-title="email"
                  item-value="id"
                  label="Related Contact"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-account"
                  clearable
                >
                  <template v-slot:item="{ props, item }">
                    <v-list-item 
                      v-bind="props" 
                      :title="`${item.raw.first_name} ${item.raw.last_name}`" 
                      :subtitle="item.raw.email"
                    ></v-list-item>
                  </template>
                </v-select>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.assigned_to"
                  :items="users"
                  item-title="username"
                  item-value="id"
                  label="Assign To"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-account-arrow-right"
                  clearable
                ></v-select>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-combobox
                  v-model="editedItem.tags"
                  label="Tags"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-tag"
                  multiple
                  chips
                  closable-chips
                  hint="Press Enter to add tags"
                  persistent-hint
                ></v-combobox>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="close" size="large">Cancel</v-btn>
          <v-btn 
            color="primary" 
            variant="flat" 
            @click="save" 
            size="large" 
            prepend-icon="mdi-content-save"
          >
            Save Task
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.task-card {
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.task-card:hover {
  transform: translateY(-4px);
  border-left-color: rgb(var(--v-theme-primary));
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
}

.overdue-card {
  border-left-color: rgb(var(--v-theme-error)) !important;
}

.overdue-card:hover {
  border-left-color: rgb(var(--v-theme-error)) !important;
}

.due-soon-card {
  border-left-color: rgb(var(--v-theme-orange)) !important;
}

.due-soon-card:hover {
  border-left-color: rgb(var(--v-theme-orange)) !important;
}

.task-details {
  min-height: 100px;
}

.task-description {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
  max-height: 4.2em;
}

.cursor-pointer {
  cursor: pointer;
}

.text-navy {
  color: #1a237e;
}

/* Ensure proper text truncation */
.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
