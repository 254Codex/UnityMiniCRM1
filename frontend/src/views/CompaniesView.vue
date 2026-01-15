<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import CompanyForm from '@/components/CompanyForm.vue'

const router = useRouter()
const companies = ref([])
const loading = ref(true)
const dialog = ref(false)
const viewMode = ref('card') // 'card' or 'table'
const search = ref('')
const selectedCompanyId = ref(null)
const formMode = ref('create') // 'create' or 'edit'

const headers = [
  { title: 'Company', key: 'name', sortable: true },
  { title: 'Industry', key: 'industry_display', sortable: true },
  { title: 'Size', key: 'company_size_display', sortable: true },
  { title: 'Email', key: 'email', sortable: false },
  { title: 'Phone', key: 'phone', sortable: false },
  { title: 'Contacts', key: 'contact_count', sortable: true, align: 'center' },
  { title: 'Deals', key: 'deal_count', sortable: true, align: 'center' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
]

onMounted(async () => {
  await loadCompanies()
})

const loadCompanies = async () => {
  loading.value = true
  try {
    const response = await api.companies.getAll()
    companies.value = response.data.map(company => ({
      ...company,
      industry_display: company.industry_display || company.industry,
      company_size_display: company.company_size_display || company.company_size,
      contact_count: company.contact_count || 0,
      deal_count: company.deal_count || 0
    }))
  } catch (error) {
    console.error('Failed to load companies:', error)
  } finally {
    loading.value = false
  }
}

const filteredCompanies = computed(() => {
  if (!search.value) return companies.value
  const searchLower = search.value.toLowerCase()
  return companies.value.filter(company =>
    company.name?.toLowerCase().includes(searchLower) ||
    company.industry?.toLowerCase().includes(searchLower) ||
    company.industry_display?.toLowerCase().includes(searchLower) ||
    company.email?.toLowerCase().includes(searchLower) ||
    company.city?.toLowerCase().includes(searchLower)
  )
})

const openCreateDialog = () => {
  selectedCompanyId.value = null
  formMode.value = 'create'
  dialog.value = true
}

const editCompany = (company) => {
  selectedCompanyId.value = company.id
  formMode.value = 'edit'
  dialog.value = true
}

const viewCompany = (company) => {
  router.push(`/companies/${company.id}`)
}

const deleteCompany = async (company) => {
  if (confirm(`Are you sure you want to delete ${company.name}?`)) {
    try {
      await api.companies.delete(company.id)
      await loadCompanies()
    } catch (error) {
      console.error('Failed to delete company:', error)
      alert('Failed to delete company. It may have associated contacts or deals.')
    }
  }
}

const getCompanyInitials = (name) => {
  if (!name) return '?'
  const words = name.split(' ')
  if (words.length >= 2) {
    return words[0][0] + words[1][0]
  }
  return name.substring(0, 2)
}

const getCompanyColor = (index) => {
  const colors = ['primary', 'secondary', 'success', 'info', 'warning', 'purple', 'pink', 'indigo']
  return colors[index % colors.length]
}

const handleFormSaved = async () => {
  dialog.value = false
  await loadCompanies()
}

const handleFormCanceled = () => {
  dialog.value = false
}

const formatCurrency = (value) => {
  if (!value) return '-'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}
</script>

<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-6 flex-wrap gap-3">
          <div>
            <h1 class="text-h3 font-weight-bold text-navy mb-2">Companies</h1>
            <p class="text-h6 text-grey-darken-1">Manage your business relationships</p>
          </div>
          <v-btn
            color="primary"
            size="large"
            prepend-icon="mdi-plus"
            @click="openCreateDialog"
            elevation="2"
          >
            Add Company
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Toolbar -->
    <v-row>
      <v-col cols="12">
        <v-card elevation="2" class="mb-4">
          <v-card-text class="pa-4">
            <div class="d-flex align-center gap-3 flex-wrap">
              <v-text-field
                v-model="search"
                prepend-inner-icon="mdi-magnify"
                label="Search companies..."
                variant="outlined"
                density="compact"
                hide-details
                clearable
                class="flex-grow-1"
                style="max-width: 400px;"
              ></v-text-field>
              
              <v-spacer></v-spacer>
              
              <v-btn-toggle
                v-model="viewMode"
                mandatory
                variant="outlined"
                divided
                density="compact"
              >
                <v-btn value="card" size="small">
                  <v-icon>mdi-view-grid</v-icon>
                </v-btn>
                <v-btn value="table" size="small">
                  <v-icon>mdi-view-list</v-icon>
                </v-btn>
              </v-btn-toggle>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-if="loading">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      </v-col>
    </v-row>

    <!-- Card View -->
    <v-row v-else-if="viewMode === 'card'">
      <v-col
        v-for="(company, index) in filteredCompanies"
        :key="company.id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <v-card elevation="3" class="company-card h-100" hover @click="viewCompany(company)" style="cursor: pointer;">
          <v-card-text class="pa-4">
            <div class="d-flex align-center mb-3">
              <v-avatar
                :color="getCompanyColor(index)"
                size="48"
                class="mr-3"
              >
                <span class="text-h6 font-weight-bold text-white">
                  {{ getCompanyInitials(company.name) }}
                </span>
              </v-avatar>
              <div class="flex-grow-1">
                <h3 class="text-h6 font-weight-bold text-truncate">{{ company.name }}</h3>
                <v-chip v-if="company.industry_display" size="x-small" variant="tonal" class="mt-1">
                  {{ company.industry_display }}
                </v-chip>
                <p v-else class="text-caption text-grey mt-1">No industry</p>
              </div>
            </div>

            <v-divider class="my-3"></v-divider>

            <div class="company-details">
              <div class="d-flex align-center justify-space-between mb-2">
                <span class="text-caption text-grey">Contacts:</span>
                <span class="text-caption font-weight-medium">{{ company.contact_count || 0 }}</span>
              </div>
              <div class="d-flex align-center justify-space-between mb-2">
                <span class="text-caption text-grey">Active Deals:</span>
                <span class="text-caption font-weight-medium">{{ company.deal_count || 0 }}</span>
              </div>
              
              <div class="d-flex align-center mb-2" v-if="company.annual_revenue">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-currency-usd</v-icon>
                <span class="text-caption text-truncate">{{ formatCurrency(company.annual_revenue) }}</span>
              </div>
              <div class="d-flex align-center mb-2" v-if="company.email">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-email</v-icon>
                <span class="text-caption text-truncate">{{ company.email }}</span>
              </div>
              <div class="d-flex align-center mb-2" v-if="company.phone">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-phone</v-icon>
                <span class="text-caption">{{ company.phone }}</span>
              </div>
              <div class="d-flex align-center" v-if="company.website">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-web</v-icon>
                <a :href="company.website" target="_blank" class="text-caption text-primary text-truncate" @click.stop>
                  {{ company.website }}
                </a>
              </div>
              
              <div class="d-flex align-center mt-2" v-if="company.city || company.country">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-map-marker</v-icon>
                <span class="text-caption text-truncate">
                  {{ [company.city, company.country].filter(Boolean).join(', ') }}
                </span>
              </div>
            </div>
          </v-card-text>

          <v-card-actions class="pa-3 pt-0" @click.stop>
            <v-btn
              size="small"
              variant="text"
              color="primary"
              prepend-icon="mdi-pencil"
              @click="editCompany(company)"
            >
              Edit
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn
              size="small"
              variant="text"
              color="error"
              icon="mdi-delete"
              @click="deleteCompany(company)"
            ></v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col v-if="filteredCompanies.length === 0" cols="12">
        <v-card elevation="2" class="pa-12">
          <div class="text-center">
            <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-office-building-outline</v-icon>
            <h3 class="text-h5 mb-2 text-grey-darken-1">No companies found</h3>
            <p class="text-body-2 text-grey mb-4">
              {{ search ? 'Try adjusting your search' : 'Get started by adding your first company' }}
            </p>
            <v-btn v-if="!search" color="primary" @click="openCreateDialog" prepend-icon="mdi-plus">
              Add Company
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
            :items="filteredCompanies"
            :loading="loading"
            :items-per-page="15"
          >
            <template v-slot:item.name="{ item, index }">
              <div class="d-flex align-center py-2">
                <v-avatar :color="getCompanyColor(index)" size="36" class="mr-3">
                  <span class="text-caption font-weight-bold text-white">
                    {{ getCompanyInitials(item.name) }}
                  </span>
                </v-avatar>
                <div>
                  <span class="font-weight-medium d-block">{{ item.name }}</span>
                  <span v-if="item.city || item.country" class="text-caption text-grey">
                    {{ [item.city, item.country].filter(Boolean).join(', ') }}
                  </span>
                </div>
              </div>
            </template>
            <template v-slot:item.industry_display="{ item }">
              <v-chip v-if="item.industry_display" size="small" variant="tonal">
                {{ item.industry_display }}
              </v-chip>
              <span v-else class="text-grey">-</span>
            </template>
            <template v-slot:item.company_size_display="{ item }">
              <span v-if="item.company_size_display">{{ item.company_size_display }}</span>
              <span v-else class="text-grey">-</span>
            </template>
            <template v-slot:item.email="{ item }">
              <span v-if="item.email">{{ item.email }}</span>
              <span v-else class="text-grey">-</span>
            </template>
            <template v-slot:item.phone="{ item }">
              <span v-if="item.phone">{{ item.phone }}</span>
              <span v-else class="text-grey">-</span>
            </template>
            <template v-slot:item.contact_count="{ item }">
              <v-chip v-if="item.contact_count > 0" size="small" color="primary" variant="flat">
                {{ item.contact_count }}
              </v-chip>
              <span v-else class="text-grey">0</span>
            </template>
            <template v-slot:item.deal_count="{ item }">
              <v-chip v-if="item.deal_count > 0" size="small" color="success" variant="flat">
                {{ item.deal_count }}
              </v-chip>
              <span v-else class="text-grey">0</span>
            </template>
            <template v-slot:item.actions="{ item }">
              <div class="d-flex">
                <v-tooltip text="View Details">
                  <template v-slot:activator="{ props }">
                    <v-icon size="small" v-bind="props" @click="viewCompany(item)" color="info" class="mr-2">mdi-eye</v-icon>
                  </template>
                </v-tooltip>
                <v-tooltip text="Edit">
                  <template v-slot:activator="{ props }">
                    <v-icon size="small" v-bind="props" @click="editCompany(item)" color="primary" class="mr-2">mdi-pencil</v-icon>
                  </template>
                </v-tooltip>
                <v-tooltip text="Delete">
                  <template v-slot:activator="{ props }">
                    <v-icon size="small" v-bind="props" @click="deleteCompany(item)" color="error">mdi-delete</v-icon>
                  </template>
                </v-tooltip>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- Company Form Dialog -->
    <v-dialog v-model="dialog" max-width="900px" persistent>
      <company-form
        v-if="dialog"
        :company-id="selectedCompanyId"
        :mode="formMode"
        @saved="handleFormSaved"
        @canceled="handleFormCanceled"
      />
    </v-dialog>
  </v-container>
</template>

<style scoped>
.company-card {
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.company-card:hover {
  transform: translateY(-4px);
  border-left-color: rgb(var(--v-theme-primary));
}

.company-details {
  min-height: 72px;
}

.text-navy {
  color: #1a237e;
}
</style>
