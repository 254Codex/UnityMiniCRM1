<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import ContactForm from '@/components/ContactForm.vue'

const router = useRouter()
const contacts = ref([])
const loading = ref(true)
const dialog = ref(false)
const viewMode = ref('card')
const search = ref('')
const selectedContactId = ref(null)
const formMode = ref('create')

const headers = [
  { title: 'Name', key: 'full_name', sortable: true },
  { title: 'Email', key: 'email', sortable: true },
  { title: 'Phone', key: 'phone', sortable: false },
  { title: 'Company', key: 'company_name', sortable: true },
  { title: 'Position', key: 'position', sortable: false },
  { title: 'Department', key: 'department', sortable: false },
  { title: 'Source', key: 'source_display', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
]

onMounted(async () => {
  await loadContacts()
})

const loadContacts = async () => {
  loading.value = true
  try {
    const response = await api.contacts.getAll()
    contacts.value = response.data.map(contact => ({
      ...contact,
      full_name: `${contact.first_name} ${contact.last_name}`,
      company_name: contact.company_details?.name || contact.company?.name,
      source_display: contact.source_display || contact.source,
      salutation_display: contact.salutation_display || contact.salutation
    }))
  } catch (error) {
    console.error('Failed to load contacts:', error)
  } finally {
    loading.value = false
  }
}

const filteredContacts = computed(() => {
  if (!search.value) return contacts.value
  const searchLower = search.value.toLowerCase()
  return contacts.value.filter(contact =>
    contact.first_name?.toLowerCase().includes(searchLower) ||
    contact.last_name?.toLowerCase().includes(searchLower) ||
    contact.email?.toLowerCase().includes(searchLower) ||
    contact.company_name?.toLowerCase().includes(searchLower) ||
    contact.position?.toLowerCase().includes(searchLower) ||
    contact.department?.toLowerCase().includes(searchLower)
  )
})

const openCreateDialog = () => {
  selectedContactId.value = null
  formMode.value = 'create'
  dialog.value = true
}

const editContact = (contact) => {
  selectedContactId.value = contact.id
  formMode.value = 'edit'
  dialog.value = true
}

const viewContact = (contact) => {
  router.push(`/contacts/${contact.id}`)
}

const deleteContact = async (contact) => {
  if (confirm(`Are you sure you want to delete ${contact.first_name} ${contact.last_name}?`)) {
    try {
      await api.contacts.delete(contact.id)
      await loadContacts()
    } catch (error) {
      console.error('Failed to delete contact:', error)
      alert('Failed to delete contact. It may have associated deals or tasks.')
    }
  }
}

const getInitials = (contact) => {
  const first = contact.first_name && contact.first_name.length > 0 ? contact.first_name[0] : ''
  const last = contact.last_name && contact.last_name.length > 0 ? contact.last_name[0] : ''
  return (first + last).toUpperCase()
}

const getAvatarColor = (index) => {
  const colors = ['primary', 'secondary', 'success', 'info', 'warning', 'purple', 'pink', 'indigo', 'teal', 'orange']
  return colors[index % colors.length]
}

const handleFormSaved = async () => {
  dialog.value = false
  await loadContacts()
}

const handleFormCanceled = () => {
  dialog.value = false
}

const getSalutationDisplay = (contact) => {
  if (contact.salutation_display) return contact.salutation_display
  if (contact.salutation) {
    const salutations = {
      'mr': 'Mr.',
      'mrs': 'Mrs.',
      'ms': 'Ms.',
      'dr': 'Dr.',
      'prof': 'Prof.'
    }
    return salutations[contact.salutation] || contact.salutation
  }
  return ''
}

const getSourceBadgeColor = (source) => {
  const colors = {
    'website': 'info',
    'referral': 'success',
    'conference': 'warning',
    'social': 'pink',
    'cold_call': 'error',
    'other': 'grey'
  }
  return colors[source] || 'grey'
}
</script>

<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-6 flex-wrap gap-3">
          <div>
            <h1 class="text-h3 font-weight-bold text-navy mb-2">Contacts</h1>
            <p class="text-h6 text-grey-darken-1">Manage your professional network</p>
          </div>
          <v-btn color="primary" size="large" prepend-icon="mdi-plus" @click="openCreateDialog" elevation="2">
            Add Contact
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
                label="Search contacts..."
                variant="outlined"
                density="compact"
                hide-details
                clearable
                class="flex-grow-1"
                style="max-width: 400px;"
              ></v-text-field>
              <v-spacer></v-spacer>
              <v-btn-toggle v-model="viewMode" mandatory variant="outlined" divided density="compact">
                <v-btn value="card" size="small"><v-icon>mdi-view-grid</v-icon></v-btn>
                <v-btn value="table" size="small"><v-icon>mdi-view-list</v-icon></v-btn>
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
      <v-col v-for="(contact, index) in filteredContacts" :key="contact.id" cols="12" sm="6" md="4" lg="3">
        <v-card elevation="3" class="contact-card h-100" hover @click="viewContact(contact)" style="cursor: pointer;">
          <v-card-text class="pa-4 text-center">
            <v-avatar :color="getAvatarColor(index)" size="64" class="mb-3">
              <span class="text-h5 font-weight-bold text-white">
                {{ getInitials(contact) }}
              </span>
            </v-avatar>
            
            <!-- Salutation & Name -->
            <div class="mb-1">
              <span v-if="contact.salutation_display || contact.salutation" class="text-caption text-grey mr-1">
                {{ getSalutationDisplay(contact) }}
              </span>
              <h3 class="text-h6 font-weight-bold d-inline">
                {{ contact.first_name }} {{ contact.last_name }}
              </h3>
            </div>
            
            <!-- Position & Department -->
            <div class="mb-2">
              <p v-if="contact.position" class="text-caption font-weight-medium mb-1">
                {{ contact.position }}
              </p>
              <p v-if="contact.department" class="text-caption text-grey">
                {{ contact.department }}
              </p>
              <p v-else-if="!contact.position" class="text-caption text-grey mb-1">No position</p>
            </div>
            
            <!-- Source Badge -->
            <v-chip v-if="contact.source_display" :color="getSourceBadgeColor(contact.source)" size="x-small" variant="tonal" class="mb-3">
              {{ contact.source_display }}
            </v-chip>
            
            <!-- Decision Maker Badge -->
            <v-chip v-if="contact.is_decision_maker" size="x-small" color="warning" variant="flat" class="mb-3 ml-1">
              <v-icon size="x-small" class="mr-1">mdi-star</v-icon>
              Decision Maker
            </v-chip>
            
            <v-divider class="my-3"></v-divider>
            
            <!-- Contact Details -->
            <div class="contact-details text-left">
              <!-- Company -->
              <div class="d-flex align-center mb-2" v-if="contact.company_name">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-office-building</v-icon>
                <span class="text-caption font-weight-medium text-truncate">{{ contact.company_name }}</span>
              </div>
              
              <!-- Email -->
              <div class="d-flex align-center mb-2" v-if="contact.email">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-email</v-icon>
                <span class="text-caption text-truncate">{{ contact.email }}</span>
              </div>
              
              <!-- Phone & Mobile -->
              <div class="d-flex align-center mb-2" v-if="contact.phone || contact.mobile">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-phone</v-icon>
                <div>
                  <div v-if="contact.phone" class="text-caption">{{ contact.phone }}</div>
                  <div v-if="contact.mobile" class="text-caption text-grey">
                    <small>Mobile: {{ contact.mobile }}</small>
                  </div>
                </div>
              </div>
              
              <!-- Social Links -->
              <div class="d-flex gap-1 mt-2">
                <v-btn v-if="contact.social_linkedin" 
                  :href="contact.social_linkedin" 
                  target="_blank" 
                  icon="mdi-linkedin" 
                  size="x-small" 
                  variant="text" 
                  color="blue"
                  @click.stop
                ></v-btn>
                <v-btn v-if="contact.social_twitter" 
                  :href="contact.social_twitter" 
                  target="_blank" 
                  icon="mdi-twitter" 
                  size="x-small" 
                  variant="text" 
                  color="light-blue"
                  @click.stop
                ></v-btn>
              </div>
            </div>
          </v-card-text>
          
          <v-card-actions class="pa-3 pt-0" @click.stop>
            <v-btn
              size="small"
              variant="text"
              color="primary"
              prepend-icon="mdi-pencil"
              @click="editContact(contact)"
            >
              Edit
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn
              size="small"
              variant="text"
              color="error"
              icon="mdi-delete"
              @click="deleteContact(contact)"
            ></v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col v-if="filteredContacts.length === 0" cols="12">
        <v-card elevation="2" class="pa-12">
          <div class="text-center">
            <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-account-outline</v-icon>
            <h3 class="text-h5 mb-2 text-grey-darken-1">No contacts found</h3>
            <p class="text-body-2 text-grey mb-4">
              {{ search ? 'Try adjusting your search' : 'Get started by adding your first contact' }}
            </p>
            <v-btn v-if="!search" color="primary" @click="openCreateDialog" prepend-icon="mdi-plus">
              Add Contact
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Table View -->
    <v-row v-else>
      <v-col cols="12">
        <v-card elevation="3">
          <v-data-table :headers="headers" :items="filteredContacts" :loading="loading" items-per-page="15">
            <!-- Name Column -->
            <template v-slot:item.full_name="{ item, index }">
              <div class="d-flex align-center py-2">
                <v-avatar :color="getAvatarColor(index)" size="36" class="mr-3">
                  <span class="text-caption font-weight-bold text-white">
                    {{ getInitials(item) }}
                  </span>
                </v-avatar>
                <div>
                  <div class="font-weight-medium d-flex align-center">
                    <span v-if="item.salutation_display || item.salutation" class="text-caption text-grey mr-1">
                      {{ getSalutationDisplay(item) }}
                    </span>
                    <span>{{ item.first_name }} {{ item.last_name }}</span>
                  </div>
                  <div v-if="item.is_decision_maker" class="text-caption">
                    <v-icon size="x-small" color="warning">mdi-star</v-icon>
                    <span class="text-warning">Decision Maker</span>
                  </div>
                </div>
              </div>
            </template>
            
            <!-- Company Column -->
            <template v-slot:item.company_name="{ item }">
              <v-chip v-if="item.company_name" size="small" variant="tonal" prepend-icon="mdi-office-building">
                {{ item.company_name }}
              </v-chip>
              <span v-else class="text-grey">-</span>
            </template>
            
            <!-- Source Column -->
            <template v-slot:item.source_display="{ item }">
              <v-chip v-if="item.source_display" 
                :color="getSourceBadgeColor(item.source)" 
                size="small" 
                variant="tonal"
              >
                {{ item.source_display }}
              </v-chip>
              <span v-else class="text-grey">-</span>
            </template>
            
            <!-- Department Column -->
            <template v-slot:item.department="{ item }">
              <span v-if="item.department">{{ item.department }}</span>
              <span v-else class="text-grey">-</span>
            </template>
            
            <!-- Actions Column -->
            <template v-slot:item.actions="{ item }">
              <div class="d-flex">
                <v-tooltip text="View Details">
                  <template v-slot:activator="{ props }">
                    <v-icon size="small" v-bind="props" @click="viewContact(item)" color="info" class="mr-2">mdi-eye</v-icon>
                  </template>
                </v-tooltip>
                <v-tooltip text="Edit">
                  <template v-slot:activator="{ props }">
                    <v-icon size="small" v-bind="props" @click="editContact(item)" color="primary" class="mr-2">mdi-pencil</v-icon>
                  </template>
                </v-tooltip>
                <v-tooltip text="Delete">
                  <template v-slot:activator="{ props }">
                    <v-icon size="small" v-bind="props" @click="deleteContact(item)" color="error">mdi-delete</v-icon>
                  </template>
                </v-tooltip>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- Contact Form Dialog -->
    <v-dialog v-model="dialog" max-width="900px" persistent>
      <contact-form
        v-if="dialog"
        :contact-id="selectedContactId"
        :mode="formMode"
        @saved="handleFormSaved"
        @canceled="handleFormCanceled"
      />
    </v-dialog>
  </v-container>
</template>

<style scoped>
.contact-card {
  transition: all 0.3s ease;
  border-top: 4px solid transparent;
}

.contact-card:hover {
  transform: translateY(-4px);
  border-top-color: rgb(var(--v-theme-primary));
}

.contact-details {
  min-height: 72px;
}

.text-navy {
  color: #1a237e;
}
</style>
