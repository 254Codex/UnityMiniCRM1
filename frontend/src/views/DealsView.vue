<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const deals = ref([])
const companies = ref([])
const contacts = ref([])
const loading = ref(true)
const dialog = ref(false)
const viewMode = ref('card')
const search = ref('')
const editedIndex = ref(-1)
const editedItem = ref({
  title: '',
  amount: 0,
  currency: 'USD',
  stage: 'lead',
  probability: 0,
  company: null,
  contact: null,
  expected_close_date: '',
  notes: '',
  tags: []
})

const defaultItem = {
  title: '',
  amount: 0,
  currency: 'USD',
  stage: 'lead',
  probability: 0,
  company: null,
  contact: null,
  expected_close_date: '',
  notes: '',
  tags: []
}

// Use constants from your API
const stageOptions = api.constants.DEAL_STAGE_CHOICES
const currencyOptions = api.constants.CURRENCY_CHOICES

const headers = [
  { title: 'Deal', key: 'title', sortable: true },
  { title: 'Amount', key: 'amount', sortable: true },
  { title: 'Stage', key: 'stage', sortable: true },
  { title: 'Probability', key: 'probability', sortable: true },
  { title: 'Company', key: 'company_name', sortable: true },
  { title: 'Contact', key: 'contact_name', sortable: false },
  { title: 'Expected Close', key: 'expected_close_date', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
]

// Computed properties
const filteredDeals = computed(() => {
  if (!search.value) return deals.value
  const searchLower = search.value.toLowerCase()
  return deals.value.filter(deal =>
    deal.title?.toLowerCase().includes(searchLower) ||
    deal.company_name?.toLowerCase().includes(searchLower) ||
    deal.contact_name?.toLowerCase().includes(searchLower) ||
    deal.stage?.toLowerCase().includes(searchLower)
  )
})

const totalPipelineValue = computed(() => {
  return deals.value.reduce((sum, deal) => sum + (deal.amount || 0), 0)
})

const weightedPipelineValue = computed(() => {
  return deals.value.reduce((sum, deal) => {
    const probability = deal.probability || 0
    return sum + ((deal.amount || 0) * (probability / 100))
  }, 0)
})

// Lifecycle
onMounted(async () => {
  await Promise.all([loadDeals(), loadCompanies(), loadContacts()])
})

// Data loading methods
const loadDeals = async () => {
  loading.value = true
  try {
    const response = await api.deals.getAll()
    deals.value = response.data.map(deal => ({
      ...deal,
      // Ensure proper field names
      company_name: deal.company?.name || '',
      contact_name: deal.contact ? `${deal.contact.first_name} ${deal.contact.last_name}` : ''
    }))
  } catch (error) {
    console.error('Failed to load deals:', error)
  } finally {
    loading.value = false
  }
}

const loadCompanies = async () => {
  try {
    const response = await api.companies.getAll({ limit: 100 })
    companies.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to load companies:', error)
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

// Utility functions
const getStageColor = (stage) => {
  const colors = {
    lead: 'blue-grey',
    qualified: 'blue',
    proposal: 'purple',
    negotiation: 'orange',
    closed_won: 'green',
    closed_lost: 'red',
    on_hold: 'grey'
  }
  return colors[stage] || 'grey'
}

const getStageLabel = (stage) => {
  const option = stageOptions.find(s => s.value === stage)
  return option ? option.label : stage.replace('_', ' ')
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value || 0)
}

const formatDate = (date) => {
  if (!date) return 'No date'
  try {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    }).format(new Date(date))
  } catch {
    return 'Invalid date'
  }
}

const formatProbability = (probability) => {
  return `${probability || 0}%`
}

const getProbabilityColor = (probability) => {
  if (probability >= 80) return 'green'
  if (probability >= 50) return 'orange'
  return 'red'
}

// CRUD operations
const editItem = (item) => {
  editedIndex.value = deals.value.findIndex(d => d.id === item.id)
  editedItem.value = {
    ...item,
    company: item.company?.id || item.company,
    contact: item.contact?.id || item.contact,
    tags: item.tags ? item.tags.split(',') : []
  }
  dialog.value = true
}

const deleteItem = async (item) => {
  if (confirm('Are you sure you want to delete this deal?')) {
    try {
      await api.deals.delete(item.id)
      await loadDeals()
    } catch (error) {
      console.error('Failed to delete deal:', error)
      alert('Failed to delete deal. Please try again.')
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
    alert('Deal title is required')
    return
  }
  
  if (!editedItem.value.amount || editedItem.value.amount <= 0) {
    alert('Amount must be greater than 0')
    return
  }
  
  if (!editedItem.value.company) {
    alert('Company is required')
    return
  }

  try {
    // Prepare data for API
    const dealData = {
      title: editedItem.value.title,
      amount: editedItem.value.amount,
      currency: editedItem.value.currency,
      stage: editedItem.value.stage,
      probability: editedItem.value.probability || 0,
      company: editedItem.value.company,
      contact: editedItem.value.contact,
      expected_close_date: editedItem.value.expected_close_date || null,
      notes: editedItem.value.notes || '',
      tags: editedItem.value.tags?.join(',') || ''
    }

    if (editedIndex.value > -1) {
      await api.deals.update(editedItem.value.id, dealData)
    } else {
      await api.deals.create(dealData)
    }
    
    await loadDeals()
    close()
  } catch (error) {
    console.error('Failed to save deal:', error)
    alert('Failed to save deal. Please check the form and try again.')
  }
}

const viewDeal = (deal) => {
  router.push(`/deals/${deal.id}`)
}

const getDealInitials = (title) => {
  if (!title) return '??'
  const words = title.split(' ')
  if (words.length >= 2) {
    return words[0][0] + words[1][0]
  }
  return title.substring(0, 2).toUpperCase()
}

const getDealColor = (index) => {
  const colors = ['primary', 'secondary', 'success', 'info', 'warning', 'purple', 'pink', 'indigo', 'teal', 'orange']
  return colors[index % colors.length]
}

// Watch for probability changes based on stage
watch(() => editedItem.value.stage, (newStage) => {
  // Set default probabilities based on stage
  const stageProbabilities = {
    lead: 10,
    qualified: 25,
    proposal: 50,
    negotiation: 75,
    closed_won: 100,
    closed_lost: 0,
    on_hold: 0
  }
  
  if (stageProbabilities[newStage] !== undefined) {
    editedItem.value.probability = stageProbabilities[newStage]
  }
})

// Handle keyboard shortcuts
const handleKeyPress = (event) => {
  if (event.ctrlKey || event.metaKey) {
    switch(event.key) {
      case 'n':
        event.preventDefault()
        dialog.value = true
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
            <h1 class="text-h3 font-weight-bold text-navy mb-2">Deals</h1>
            <p class="text-h6 text-grey-darken-1">Track your sales pipeline</p>
            <div class="d-flex align-center gap-4 mt-2">
              <div>
                <span class="text-caption text-grey-darken-1">Pipeline Value:</span>
                <span class="text-h6 font-weight-bold text-green ml-2">{{ formatCurrency(totalPipelineValue) }}</span>
              </div>
              <div>
                <span class="text-caption text-grey-darken-1">Weighted Value:</span>
                <span class="text-h6 font-weight-bold text-blue ml-2">{{ formatCurrency(weightedPipelineValue) }}</span>
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
              Add Deal
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
                label="Search deals..."
                variant="outlined"
                density="compact"
                hide-details
                clearable
                class="flex-grow-1"
                style="max-width: 400px;"
              ></v-text-field>
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
        <p class="mt-4 text-body-1 text-grey">Loading deals...</p>
      </v-col>
    </v-row>

    <!-- Card View -->
    <v-row v-else-if="viewMode === 'card'">
      <v-col 
        v-for="(deal, index) in filteredDeals" 
        :key="deal.id" 
        cols="12" 
        sm="6" 
        md="4" 
        lg="3"
      >
        <v-card 
          elevation="3" 
          class="deal-card h-100 cursor-pointer"
          hover
          @click="viewDeal(deal)"
        >
          <v-card-text class="pa-4">
            <div class="d-flex align-center mb-3">
              <v-avatar :color="getDealColor(index)" size="48" class="mr-3">
                <span class="text-h6 font-weight-bold text-white">
                  {{ getDealInitials(deal.title) }}
                </span>
              </v-avatar>
              <div class="flex-grow-1">
                <h3 class="text-h6 font-weight-bold text-truncate mb-1">{{ deal.title }}</h3>
                <v-chip 
                  :color="getStageColor(deal.stage)" 
                  size="x-small" 
                  variant="flat" 
                  class="text-capitalize font-weight-bold"
                >
                  {{ getStageLabel(deal.stage) }}
                </v-chip>
              </div>
            </div>

            <v-divider class="my-3"></v-divider>

            <div class="deal-details">
              <div class="d-flex align-center justify-space-between mb-3">
                <span class="text-overline text-grey-darken-1">Deal Value</span>
                <span class="text-h5 font-weight-bold text-green">{{ formatCurrency(deal.amount) }}</span>
              </div>

              <div class="d-flex align-center justify-space-between mb-3">
                <span class="text-overline text-grey-darken-1">Probability</span>
                <v-chip 
                  :color="getProbabilityColor(deal.probability)" 
                  size="x-small" 
                  variant="flat"
                  class="font-weight-bold"
                >
                  {{ formatProbability(deal.probability) }}
                </v-chip>
              </div>

              <div class="d-flex align-center mb-2" v-if="deal.company_name">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-office-building</v-icon>
                <span class="text-caption font-weight-medium text-truncate">{{ deal.company_name }}</span>
              </div>

              <div class="d-flex align-center mb-2" v-if="deal.contact_name">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-account</v-icon>
                <span class="text-caption text-truncate">{{ deal.contact_name }}</span>
              </div>

              <div class="d-flex align-center" v-if="deal.expected_close_date">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-calendar</v-icon>
                <span class="text-caption">{{ formatDate(deal.expected_close_date) }}</span>
              </div>
            </div>
          </v-card-text>
          <v-card-actions class="pa-3 pt-0">
            <v-btn 
              size="small" 
              variant="text" 
              color="primary" 
              prepend-icon="mdi-pencil"
              @click.stop="editItem(deal)"
            >
              Edit
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn 
              size="small" 
              variant="text" 
              color="error" 
              icon="mdi-delete"
              @click.stop="deleteItem(deal)"
            ></v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <!-- Empty State -->
      <v-col v-if="filteredDeals.length === 0" cols="12">
        <v-card elevation="2" class="pa-12">
          <div class="text-center">
            <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-handshake-outline</v-icon>
            <h3 class="text-h5 mb-2 text-grey-darken-1">No deals found</h3>
            <p class="text-body-2 text-grey mb-4">
              {{ search ? 'Try adjusting your search' : 'Get started by adding your first deal' }}
            </p>
            <v-btn v-if="!search" color="primary" @click="dialog = true" prepend-icon="mdi-plus">
              Add Your First Deal
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
            :items="filteredDeals" 
            :loading="loading" 
            items-per-page="15"
            class="elevation-1"
          >
            <template v-slot:item.title="{ item, index }">
              <div class="d-flex align-center py-2 cursor-pointer" @click="viewDeal(item)">
                <v-avatar :color="getDealColor(index)" size="36" class="mr-3">
                  <span class="text-caption font-weight-bold text-white">
                    {{ getDealInitials(item.title) }}
                  </span>
                </v-avatar>
                <div>
                  <span class="font-weight-medium d-block">{{ item.title }}</span>
                  <span class="text-caption text-grey">#{{ item.deal_code || item.id.slice(0, 8) }}</span>
                </div>
              </div>
            </template>
            <template v-slot:item.amount="{ item }">
              <span class="font-weight-bold text-green">{{ formatCurrency(item.amount) }}</span>
            </template>
            <template v-slot:item.stage="{ item }">
              <v-chip 
                :color="getStageColor(item.stage)" 
                size="small" 
                variant="flat" 
                class="text-capitalize font-weight-bold"
              >
                {{ getStageLabel(item.stage) }}
              </v-chip>
            </template>
            <template v-slot:item.probability="{ item }">
              <v-progress-linear
                :model-value="item.probability || 0"
                :color="getProbabilityColor(item.probability)"
                height="8"
                rounded
                class="my-2"
              >
                <template v-slot:default>
                  <span class="text-caption font-weight-bold">
                    {{ formatProbability(item.probability) }}
                  </span>
                </template>
              </v-progress-linear>
            </template>
            <template v-slot:item.company_name="{ item }">
              <v-chip v-if="item.company_name" size="small" variant="tonal" prepend-icon="mdi-office-building">
                {{ item.company_name }}
              </v-chip>
              <span v-else class="text-grey">-</span>
            </template>
            <template v-slot:item.contact_name="{ item }">
              <v-chip v-if="item.contact_name" size="small" variant="tonal" prepend-icon="mdi-account">
                {{ item.contact_name }}
              </v-chip>
              <span v-else class="text-grey">-</span>
            </template>
            <template v-slot:item.expected_close_date="{ item }">
              <span v-if="item.expected_close_date" class="font-weight-medium">
                {{ formatDate(item.expected_close_date) }}
              </span>
              <span v-else class="text-grey">-</span>
            </template>
            <template v-slot:item.actions="{ item }">
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
                <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-handshake-outline</v-icon>
                <h3 class="text-h5 mb-2 text-grey-darken-1">No deals found</h3>
                <p class="text-body-2 text-grey mb-4">
                  {{ search ? 'Try adjusting your search' : 'Get started by adding your first deal' }}
                </p>
                <v-btn v-if="!search" color="primary" @click="dialog = true" prepend-icon="mdi-plus">
                  Add Deal
                </v-btn>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- Deal Dialog -->
    <v-dialog v-model="dialog" max-width="800px" persistent>
      <v-card>
        <v-card-title class="pa-4 bg-grey-lighten-4">
          <div class="d-flex align-center">
            <v-icon class="mr-2" color="primary">
              {{ editedIndex === -1 ? 'mdi-handshake-outline' : 'mdi-handshake' }}
            </v-icon>
            <span class="text-h6 font-weight-bold">
              {{ editedIndex === -1 ? 'New Deal' : 'Edit Deal' }}
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
                  label="Deal Title *"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-text"
                  required
                  :rules="[v => !!v || 'Title is required']"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="editedItem.amount"
                  label="Amount *"
                  type="number"
                  prefix="$"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-currency-usd"
                  required
                  :rules="[
                    v => !!v || 'Amount is required',
                    v => v > 0 || 'Amount must be greater than 0'
                  ]"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.currency"
                  :items="currencyOptions"
                  label="Currency"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-cash"
                ></v-select>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.stage"
                  :items="stageOptions"
                  label="Stage *"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-chart-timeline-variant"
                  required
                  :rules="[v => !!v || 'Stage is required']"
                ></v-select>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-slider
                  v-model="editedItem.probability"
                  label="Probability"
                  color="primary"
                  thumb-label
                  :max="100"
                  :min="0"
                  :step="5"
                  prepend-icon="mdi-percent"
                >
                  <template v-slot:append>
                    <span class="text-h6 font-weight-bold">{{ editedItem.probability }}%</span>
                  </template>
                </v-slider>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.company"
                  :items="companies"
                  item-title="name"
                  item-value="id"
                  label="Company *"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-office-building"
                  required
                  :rules="[v => !!v || 'Company is required']"
                >
                  <template v-slot:item="{ props, item }">
                    <v-list-item v-bind="props" :title="item.raw.name" :subtitle="item.raw.industry"></v-list-item>
                  </template>
                </v-select>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.contact"
                  :items="contacts"
                  item-title="email"
                  item-value="id"
                  label="Contact"
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
                  <template v-slot:selection="{ item }">
                    {{ item.raw.first_name }} {{ item.raw.last_name }}
                  </template>
                </v-select>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="editedItem.expected_close_date"
                  label="Expected Close Date"
                  type="date"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-calendar"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="editedItem.notes"
                  label="Notes"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-note-text"
                  rows="3"
                  auto-grow
                ></v-textarea>
              </v-col>
              
              <v-col cols="12">
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
            Save Deal
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.deal-card {
  transition: all 0.3s ease;
  border-top: 4px solid transparent;
}

.deal-card:hover {
  transform: translateY(-4px);
  border-top-color: rgb(var(--v-theme-primary));
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
}

.deal-details {
  min-height: 120px;
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
