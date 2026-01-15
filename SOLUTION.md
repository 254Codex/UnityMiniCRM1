# **Mini CRM Application - Technical Solution**

## **📋 Feature Choice & Rationale**

### **Core Features Implemented**

#### **1. Dashboard with Analytics** ✅
**Rationale**: The dashboard is the nerve center of any CRM system. It provides:
- Real-time visibility into business performance
- Quick decision-making capabilities
- User engagement through visual data representation
- Immediate value recognition for stakeholders

#### **2. Contact & Company Management** ✅
**Rationale**: Fundamental CRM operations:
- **Contacts** represent individual relationships
- **Companies** represent organizational relationships
- CRUD operations with soft delete for data recovery
- Advanced filtering and search for large datasets

#### **3. Deal Pipeline Management** ✅
**Rationale**: Core revenue tracking:
- Visual sales pipeline with stage progression
- Probability-based revenue forecasting
- Deal value tracking with currency support
- Expected close date management

#### **4. Task Management** ✅
**Rationale**: Operational efficiency:
- Task prioritization (Urgent/High/Medium/Low)
- Status tracking (Pending/In Progress/Completed)
- Deadline management with overdue alerts
- Relationship to contacts/deals for context

#### **5. Modern UX/UI Design** ✅
**Rationale**: User adoption and satisfaction:
- Material Design with Vuetify 3
- Responsive design for all devices
- Dark/Light theme support
- Keyboard shortcuts for power users
- Progressive Web App capabilities

### **Features Prioritized for MVP**

1. **Essential** (Implemented):
   - User authentication
   - Basic CRUD operations
   - Dashboard analytics
   - Responsive design

2. **Important** (Implemented):
   - Advanced filtering
   - Export functionality
   - Real-time updates
   - Data validation

3. **Nice-to-have** (Future):
   - Email integration
   - Document management
   - Calendar synchronization
   - Advanced reporting

---

## **🔧 Technical Approach & Design Decisions**

### **Architecture Pattern: Clean Architecture**

```
┌─────────────────────────────────────┐
│         Presentation Layer          │
│  (Vue.js Components + Vuetify)      │
├─────────────────────────────────────┤
│         Application Layer           │
│  (Services, Composables, Stores)    │
├─────────────────────────────────────┤
│          Domain Layer               │
│  (Business Logic, Models)           │
├─────────────────────────────────────┤
│         Infrastructure Layer        │
│  (Django ORM, API, Database)        │
└─────────────────────────────────────┘
```

### **Backend Design Decisions**

#### **1. Django REST Framework Choice**
- **Why Django?**: Batteries-included framework with built-in admin, ORM, and security
- **Why REST Framework?**: Rapid API development with serializers, viewsets, and authentication
- **Alternative Considered**: FastAPI (chosen Django for its maturity and ecosystem)

#### **2. UUID Primary Keys**
```python
id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
```
- **Decision**: Use UUID instead of sequential IDs
- **Rationale**:
  - Security through obscurity
  - Prevents ID enumeration attacks
  - Easier database merges and replication
  - No revealing business information through IDs

#### **3. Soft Delete Implementation**
```python
is_active = models.BooleanField(default=True)

def delete(self, *args, **kwargs):
    """Soft delete - mark as inactive"""
    self.is_active = False
    self.save()
```
- **Decision**: Never physically delete user data
- **Rationale**:
  - Data recovery capability
  - Audit trail maintenance
  - Compliance with data retention policies
  - Historical analysis preservation

#### **4. Token-Based Authentication**
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
```
- **Decision**: Token auth over session/cookie auth
- **Rationale**:
  - Stateless architecture
  - Better for mobile/SPA applications
  - Easier to scale horizontally
  - No CSRF protection needed

### **Frontend Design Decisions**

#### **1. Vue 3 with Composition API**
```javascript
// Instead of Options API
export default {
  data() { return { count: 0 } },
  methods: { increment() { this.count++ } }
}

// Using Composition API
import { ref } from 'vue'
export default {
  setup() {
    const count = ref(0)
    const increment = () => count.value++
    return { count, increment }
  }
}
```
- **Decision**: Composition API over Options API
- **Rationale**:
  - Better TypeScript support
  - More flexible code organization
  - Reusable composition functions
  - Better long-term maintainability

#### **2. Vuetify 3 for UI Components**
- **Decision**: Vuetify over other UI libraries (Quasar, Element Plus)
- **Rationale**:
  - Material Design implementation
  - Extensive component library
  - Good Vue 3 support
  - Active community and documentation
  - Built-in accessibility features

#### **3. Axios for API Communication**
```javascript
// Centralized API service
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

// Request interceptor for auth token
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Token ${token}`
  return config
})
```
- **Decision**: Axios over Fetch API
- **Rationale**:
  - Request/response interceptors
  - Timeout configuration
  - Automatic JSON parsing
  - Browser compatibility
  - Request cancellation

#### **4. File-Based Routing with Vue Router**
```javascript
const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true, title: 'Dashboard - CRM' }
  }
]
```
- **Decision**: File-based routing over configuration-based
- **Rationale**:
  - Clear separation of concerns
  - Automatic code splitting
  - Easy navigation guards
  - Meta field support for SEO

---

## **⚙️ Implementation Details**

### **Backend Implementation**

#### **1. Model Relationships**
```python
# apps/companies/models.py
class Company(models.Model):
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Many-to-one relationships maintained

# apps/contacts/models.py  
class Contact(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contacts')
    # Cascade delete: contacts removed when company is deleted
```

#### **2. Serializer Design**
```python
class CompanySerializer(serializers.ModelSerializer):
    # Computed fields
    contact_count = serializers.SerializerMethodField()
    deal_count = serializers.SerializerMethodField()
    total_deal_value = serializers.SerializerMethodField()
    
    # Nested relationships
    contacts = ContactSerializer(many=True, read_only=True)
    deals = DealSerializer(many=True, read_only=True)
    
    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')
    
    def get_contact_count(self, obj):
        return obj.contacts.count()
    
    def create(self, validated_data):
        # Auto-assign created_by from request user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
```

#### **3. ViewSet with Custom Actions**
```python
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.filter(is_active=True)
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['industry', 'company_size', 'country']
    search_fields = ['name', 'email', 'phone', 'city']
    
    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        company = self.get_object()
        contacts = company.contacts.filter(is_active=True)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def deals(self, request, pk=None):
        company = self.get_object()
        deals = company.deals.filter(status='active')
        serializer = DealSerializer(deals, many=True)
        return Response(serializer.data)
```

#### **4. Performance Optimizations**
```python
# Using select_related and prefetch_related
queryset = Company.objects.select_related(
    'assigned_to', 'created_by'
).prefetch_related(
    Prefetch('contacts', queryset=Contact.objects.filter(is_active=True)),
    Prefetch('deals', queryset=Deal.objects.filter(status='active'))
)

# Database indexing
class Meta:
    indexes = [
        models.Index(fields=['name']),
        models.Index(fields=['industry']),
        models.Index(fields=['created_at']),
        models.Index(fields=['assigned_to', 'is_active']),
    ]
```

### **Frontend Implementation**

#### **1. Component Architecture**
```
src/components/
├── layout/           # Layout components (Header, Sidebar, Footer)
├── ui/              # Reusable UI components (Cards, Tables, Forms)
├── forms/           # Form components with validation
└── charts/          # Chart components for dashboard
```

#### **2. State Management Strategy**
```javascript
// Using Pinia for global state
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: !!localStorage.getItem('token')
  }),
  
  actions: {
    async login(credentials) {
      const response = await api.auth.login(credentials)
      this.user = response.data.user
      this.token = response.data.token
      this.isAuthenticated = true
      localStorage.setItem('token', this.token)
    },
    
    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      localStorage.removeItem('token')
    }
  }
})
```

#### **3. API Service Layer**
```javascript
// services/api.js - Centralized API management
export default {
  // Authentication
  auth: {
    login(credentials) {
      return apiClient.post('auth/login/', credentials)
    },
    logout() {
      return apiClient.post('auth/logout/')
    }
  },
  
  // Companies
  companies: {
    getAll(params = {}) {
      return apiClient.get('companies/', { params })
    },
    get(id) {
      return apiClient.get(`companies/${id}/`)
    },
    create(data) {
      return apiClient.post('companies/', data)
    },
    update(id, data) {
      return apiClient.put(`companies/${id}/`, data)
    }
  }
}
```

#### **4. Form Handling with Validation**
```vue
<script setup>
import { useForm } from 'vee-validate'
import * as yup from 'yup'

const schema = yup.object({
  name: yup.string().required('Company name is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  phone: yup.string().matches(/^[0-9+\-\s()]+$/, 'Invalid phone number')
})

const { handleSubmit, errors } = useForm({ validationSchema: schema })

const onSubmit = handleSubmit(async (values) => {
  try {
    await api.companies.create(values)
    // Success handling
  } catch (error) {
    // Error handling
  }
})
</script>
```

#### **5. Real-time Features Implementation**
```javascript
// WebSocket connection for real-time updates
const setupWebSocket = () => {
  const socket = new WebSocket(`ws://${window.location.host}/ws/notifications/`)
  
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data)
    switch(data.type) {
      case 'task_assigned':
        showNotification(`New task: ${data.task.title}`)
        break
      case 'deal_updated':
        updateDealInStore(data.deal)
        break
    }
  }
  
  return () => socket.close()
}
```

---

## **🚧 Challenges & Trade-offs**

### **1. Database Design Challenges**

**Challenge**: Managing complex relationships between entities
```python
# Circular dependency issue
# Contact references Company, Deal references Contact and Company
# Task references Contact, Deal, and Company

# Solution: Use string references in ForeignKey
company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
```

**Challenge**: Soft delete with cascading
```python
# Trade-off: Manual cascade handling needed
def delete(self, *args, **kwargs):
    self.is_active = False
    self.save()
    # Manually soft delete related objects
    self.contacts.update(is_active=False)
    self.deals.update(status='inactive')
```

### **2. API Performance Trade-offs**

**Trade-off**: Nested serializers vs separate endpoints
```python
# Option 1: Nested serializers (convenient but heavy)
class CompanySerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)
    deals = DealSerializer(many=True, read_only=True)
    # Pro: Single request gets all data
    # Con: Large response payload, N+1 query problems

# Option 2: Separate endpoints (chosen)
GET /api/companies/           # Lightweight company list
GET /api/companies/{id}/      # Company details
GET /api/companies/{id}/contacts/  # Company contacts
# Pro: Smaller payloads, better caching
# Con: More API calls from frontend
```

### **3. Frontend State Management**

**Challenge**: Keeping UI in sync with backend data
```javascript
// Trade-off: Optimistic updates vs waiting for API response

// Option 1: Optimistic update (chosen for better UX)
addContact(contact) {
  // Update UI immediately
  this.contacts.push(contact)
  
  // Then call API
  api.contacts.create(contact).catch(error => {
    // Rollback on error
    this.contacts.pop()
    showError('Failed to add contact')
  })
}

// Option 2: Wait for API response
async addContact(contact) {
  try {
    const response = await api.contacts.create(contact)
    this.contacts.push(response.data)  // Wait for success
  } catch (error) {
    showError('Failed to add contact')
  }
}
```

### **4. Authentication Security**

**Challenge**: Token storage security
```javascript
// Trade-off: LocalStorage vs Cookies

// Option 1: LocalStorage (chosen for simplicity)
localStorage.setItem('token', token)
// Pro: Easy implementation, works with SPA
// Con: Vulnerable to XSS attacks

// Option 2: HttpOnly Cookies
// Pro: More secure against XSS
// Con: Requires CSRF protection, CORS configuration
// Con: Harder to implement with token-based auth

// Mitigation for LocalStorage:
// - Use short-lived tokens (24h)
// - Implement token refresh
// - Add XSS protection headers
// - Use Content Security Policy
```

### **5. Responsive Design Challenges**

**Challenge**: Complex data tables on mobile
```vue
<!-- Trade-off: Card view vs Table view -->
<template>
  <!-- Mobile: Card view (better for touch) -->
  <div v-if="isMobile" class="card-view">
    <v-card v-for="contact in contacts" :key="contact.id">
      <!-- Compact card layout -->
    </v-card>
  </div>
  
  <!-- Desktop: Table view (better for scanning) -->
  <v-data-table v-else :items="contacts" :headers="headers">
    <!-- Full table with all columns -->
  </v-data-table>
</template>

<script>
const isMobile = computed(() => window.innerWidth < 960)
</script>
```

---

## **🛠️ Setup & Testing Instructions**

### **Complete Setup Guide**

#### **1. Prerequisites Installation**
```bash
# Install Python 3.8+
python --version
# Python 3.8.0 or higher required

# Install Node.js 18+
node --version
# Node.js 18.0.0 or higher required

# Install PostgreSQL (optional, SQLite works for development)
sudo apt-get install postgresql postgresql-contrib  # Ubuntu
brew install postgresql                            # macOS
```

#### **2. Backend Setup**
```bash
# Clone repository
git clone https://github.com/254Codex/UnityMiniCRM1.git
cd interview/backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings:
# DEBUG=True
# SECRET_KEY=your-secret-key-here
# DATABASE_URL=sqlite:///db.sqlite3
# ALLOWED_HOSTS=localhost,127.0.0.1

# Set up database
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
# Follow prompts to create admin account

# Load sample data (optional)
python manage.py loaddata sample_data.json

# Run development server
python manage.py runserver
# Server runs at http://localhost:8000
# Admin panel: http://localhost:8000/admin
```

#### **3. Frontend Setup**
```bash
cd ../frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env:
# VITE_API_URL=http://localhost:8000/api
# VITE_APP_NAME=Mini CRM

# Run development server
npm run dev
# Frontend runs at http://localhost:5173
```

#### **4. Docker Setup (Alternative)**
```bash
# From project root
docker-compose up -d

# Check running containers
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop containers
docker-compose down
```

### **Testing Instructions**

#### **1. Backend Tests**
```bash
cd backend

# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.companies
python manage.py test apps.contacts

# Run with coverage
coverage run manage.py test
coverage report
coverage html  # Generate HTML report

# API testing with curl
curl -X GET http://localhost:8000/api/companies/ \
  -H "Authorization: Token your-token-here"

# Create test data
curl -X POST http://localhost:8000/api/companies/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Company", "industry": "technology"}'
```

#### **2. Frontend Tests**
```bash
cd frontend

# Unit tests
npm run test:unit

# Component tests
npm run test:component

# E2E tests (if configured)
npm run test:e2e

# Linting
npm run lint
npm run lint:fix

# Type checking (if using TypeScript)
npm run type-check
```

#### **3. Manual Testing Scenarios**

**Test 1: User Authentication**
```
1. Navigate to http://localhost:5173/login
2. Enter credentials:
   - Username: demo
   - Password: demo123
3. Verify successful login and redirect to dashboard
4. Verify token is stored in localStorage
5. Logout and verify token is removed
```

**Test 2: CRUD Operations**
```
1. Create a new company
   - Click "Add Company"
   - Fill form with test data
   - Verify success message
   - Verify company appears in list

2. Edit the company
   - Click edit on the company
   - Change name/industry
   - Verify changes are saved
   - Verify updated data in list

3. Delete the company (soft delete)
   - Click delete on the company
   - Confirm deletion
   - Verify company disappears from active list
   - Verify company still exists in database
```

**Test 3: Dashboard Functionality**
```
1. Load dashboard
2. Verify all statistics cards show data
3. Verify deals by stage chart renders
4. Verify recent tasks list shows items
5. Verify quick actions work
6. Test dark/light theme toggle
```

**Test 4: Responsive Design**
```
1. Test on desktop (width > 960px)
   - Verify sidebar is visible
   - Verify table view for lists
   - Verify all features accessible

2. Test on tablet (width 600px - 960px)
   - Verify responsive adjustments
   - Verify navigation works
   - Verify readable layout

3. Test on mobile (width < 600px)
   - Verify hamburger menu works
   - Verify card view for lists
   - Verify touch-friendly controls
```

#### **4. API Testing with Postman/Insomnia**

**Collection Setup:**
```json
{
  "auth": {
    "login": "POST /api/auth/login/",
    "logout": "POST /api/auth/logout/",
    "refresh": "POST /api/auth/refresh/"
  },
  "companies": {
    "list": "GET /api/companies/",
    "create": "POST /api/companies/",
    "detail": "GET /api/companies/{id}/",
    "update": "PUT /api/companies/{id}/",
    "delete": "DELETE /api/companies/{id}/"
  }
}
```

**Test Script:**
```javascript
// Postman test script
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response time is less than 500ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(500);
});

pm.test("Response has correct content type", function () {
    pm.response.to.have.header("Content-Type", "application/json");
});
```

---

## **🔮 Future Improvements**

### **1. Enhanced Features**

#### **Email Integration**
```python
# apps/email_integration/models.py
class EmailIntegration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email_provider = models.CharField(choices=EMAIL_PROVIDERS)
    access_token = models.TextField(encrypted=True)  # Encrypted storage
    refresh_token = models.TextField(encrypted=True)
    is_active = models.BooleanField(default=True)
    
    # Features:
    # - Send emails from CRM
    # - Track email opens/clicks
    # - Auto-log email communications
    # - Email templates
```

#### **Document Management**
```python
# apps/documents/models.py
class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    file_type = models.CharField(max_length=50)
    file_size = models.IntegerField()
    related_to = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    related_id = models.UUIDField()
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tags = models.CharField(max_length=500)
    
    # Features:
    # - Version control
    # - OCR for scanned documents
    # - Full-text search
    # - Secure access control
```

#### **Advanced Reporting**
```python
# apps/reports/models.py
class Report(models.Model):
    name = models.CharField(max_length=255)
    report_type = models.CharField(choices=REPORT_TYPES)
    filters = models.JSONField()  # Store filter criteria
    schedule = models.CharField(choices=SCHEDULE_CHOICES, null=True, blank=True)
    recipients = models.ManyToManyField(User)
    last_run = models.DateTimeField(null=True, blank=True)
    
    # Features:
    # - Custom report builder
    # - Scheduled email reports
    # - Export to PDF/Excel
    # - Dashboard widgets
```

### **2. Performance Optimizations**

#### **GraphQL Implementation**
```python
# Replace REST with GraphQL for flexible queries
import graphene
from graphene_django import DjangoObjectType

class CompanyType(DjangoObjectType):
    class Meta:
        model = Company
        fields = '__all__'
    
    contacts = graphene.List(ContactType)
    deals = graphene.List(DealType)
    
    def resolve_contacts(self, info):
        return self.contacts.filter(is_active=True)
    
    def resolve_deals(self, info):
        return self.deals.filter(status='active')
```

#### **Real-time Database**
```python
# Implement change data capture
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Deal)
def deal_updated(sender, instance, created, **kwargs):
    # Send WebSocket notification
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'deals_{instance.company_id}',
        {
            'type': 'deal_update',
            'deal': DealSerializer(instance).data
        }
    )
```

#### **Advanced Caching Strategy**
```python
# Redis caching with invalidation
from django.core.cache import cache

class CompanyViewSet(viewsets.ModelViewSet):
    
    def get_queryset(self):
        cache_key = f'companies_{self.request.user.id}_{self.request.GET.urlencode()}'
        companies = cache.get(cache_key)
        
        if not companies:
            companies = super().get_queryset()
            cache.set(cache_key, companies, timeout=300)  # 5 minutes
        
        return companies
    
    def perform_create(self, serializer):
        instance = serializer.save()
        # Invalidate cache
        cache.delete_pattern(f'companies_{self.request.user.id}_*')
        return instance
```

### **3. Security Enhancements**

#### **Two-Factor Authentication**
```python
# apps/auth/views.py
class TwoFactorView(APIView):
    def post(self, request):
        # Generate and send OTP
        otp = generate_otp()
        send_sms(request.user.phone, f'Your OTP: {otp}')
        
        # Store OTP hash in session
        request.session['2fa_otp'] = hash_otp(otp)
        request.session['2fa_expiry'] = timezone.now() + timedelta(minutes=5)
        
        return Response({'message': 'OTP sent'})
```

#### **Audit Logging**
```python
# apps/audit/models.py
class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)  # CREATE, UPDATE, DELETE, VIEW
    model = models.CharField(max_length=100)
    object_id = models.UUIDField()
    changes = models.JSONField()  # Store before/after data
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['model', 'object_id']),
        ]
```

### **4. Scalability Improvements**

#### **Microservices Architecture**
```
crm-system/
├── auth-service/          # Authentication service
├── company-service/       # Company management
├── contact-service/       # Contact management
├── deal-service/         # Deal management
├── task-service/         # Task management
├── notification-service/ # Notifications
├── api-gateway/          # API Gateway
└── message-broker/       # RabbitMQ/Kafka
```

#### **Database Sharding**
```python
# Shard by company or region
class CompanyRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'companies':
            # Route based on company region
            if 'instance' in hints:
                return f'db_{hints["instance"].region}'
        return None
```

### **5. Mobile Application**

#### **React Native Mobile App**
```javascript
// Mobile app with React Native
import React from 'react';
import {View, Text, FlatList} from 'react-native';
import {useQuery} from 'react-query';

const ContactsScreen = () => {
  const {data: contacts} = useQuery('contacts', fetchContacts);
  
  return (
    <FlatList
      data={contacts}
      renderItem={({item}) => (
        <ContactCard contact={item} />
      )}
    />
  );
};
```

#### **Offline Capability**
```javascript
// Service worker for offline functionality
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/api/')) {
    // Cache API responses
    event.respondWith(
      caches.match(event.request)
        .then(response => response || fetch(event.request))
    );
  }
});
```

---

## **🗄️ Database Migrations**

### **Migration Strategy**

#### **1. Initial Migration**
```bash
# Generate initial migrations
python manage.py makemigrations companies
python manage.py makemigrations contacts
python manage.py makemigrations deals
python manage.py makemigrations tasks
python manage.py makemigrations interactions

# Apply migrations
python manage.py migrate
```

#### **2. Sample Migration Files**

**Companies Migration:**
```python
# apps/companies/migrations/0001_initial.py
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('industry', models.CharField(choices=[('technology', 'Technology'), ('finance', 'Finance'), ('healthcare', 'Healthcare'), ('education', 'Education'), ('retail', 'Retail'), ('manufacturing', 'Manufacturing'), ('consulting', 'Consulting'), ('other', 'Other')], default='other', max_length=50)),
                ('company_size', models.CharField(blank=True, choices=[('micro', 'Micro (1-9)'), ('small', 'Small (10-49)'), ('medium', 'Medium (50-249)'), ('large', 'Large (250+)')], max_length=20, null=True)),
                ('website', models.URLField(blank=True, max_length=500)),
                ('phone', models.CharField(blank=True, max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('address', models.TextField(blank=True)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('state', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('postal_code', models.CharField(blank=True, max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('tags', models.CharField(blank=True, max_length=500)),
                ('annual_revenue', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('founded_year', models.IntegerField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_companies', to='users.user')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_companies', to='users.user')),
            ],
            options={
                'verbose_name_plural': 'Companies',
                'ordering': ['name'],
                'indexes': [models.Index(fields=['name'], name='company_name_idx'), models.Index(fields=['industry'], name='company_industry_idx'), models.Index(fields=['created_at'], name='company_created_idx')],
            },
        ),
    ]
```

**Contacts Migration:**
```python
# apps/contacts/migrations/0001_initial.py
class Migration(migrations.Migration):
    dependencies = [
        ('companies', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('salutation', models.CharField(blank=True, choices=[('mr', 'Mr.'), ('mrs', 'Mrs.'), ('ms', 'Ms.'), ('dr', 'Dr.'), ('prof', 'Prof.')], max_length=10)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=50)),
                ('mobile', models.CharField(blank=True, max_length=50)),
                ('position', models.CharField(blank=True, max_length=200)),
                ('department', models.CharField(blank=True, max_length=200)),
                ('source', models.CharField(choices=[('website', 'Website'), ('referral', 'Referral'), ('conference', 'Conference'), ('social', 'Social Media'), ('cold_call', 'Cold Call'), ('other', 'Other')], default='other', max_length=50)),
                ('is_decision_maker', models.BooleanField(default=False)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('tags', models.CharField(blank=True, max_length=500)),
                ('social_linkedin', models.URLField(blank=True, max_length=500)),
                ('social_twitter', models.URLField(blank=True, max_length=500)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_contacts', to='users.user')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='companies.company')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_contacts', to='users.user')),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
                'indexes': [models.Index(fields=['last_name', 'first_name'], name='contact_name_idx'), models.Index(fields=['email'], name='contact_email_idx'), models.Index(fields=['company', 'is_active'], name='contact_company_idx')],
                'unique_together': {('email', 'company')},
            },
        ),
    ]
```

#### **3. Data Migration Example**
```python
# apps/companies/migrations/0002_add_default_tags.py
from django.db import migrations

def add_default_tags(apps, schema_editor):
    Company = apps.get_model('companies', 'Company')
    
    # Add default tags to companies without tags
    for company in Company.objects.filter(tags=''):
        company.tags = 'prospect,customer,vendor'
        company.save()

class Migration(migrations.Migration):
    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_default_tags),
    ]
```

#### **4. Database Rollback Plan**
```bash
# Check migration status
python manage.py showmigrations

# Rollback specific migration
python manage.py migrate companies 0001

# Rollback all app migrations
python manage.py migrate companies zero

# Create migration checkpoint
python manage.py makemigrations --empty companies --name backup_pre_changes
```

#### **5. Production Migration Checklist**
```bash
# 1. Backup database
python manage.py dumpdata --indent=2 > backup_$(date +%Y%m%d).json

# 2. Check migration conflicts
python manage.py makemigrations --check --dry-run

# 3. Run migrations on test database
python manage.py migrate --database=test

# 4. Run data migrations
python manage.py runscript data_migration_script

# 5. Verify migration success
python manage.py dbs