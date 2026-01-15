# **Mini CRM Application**

A professional, full-stack Customer Relationship Management (CRM) system built with Django REST Framework and Vue.js 3. This enterprise-grade solution provides comprehensive tools for managing customer relationships, sales pipelines, and business operations.

## **🚀 Tech Stack**

### **Backend (Django)**
- **Django 4.2.7** - Robust Python web framework
- **Django REST Framework 3.14** - Full-featured REST API toolkit
- **PostgreSQL** / **SQLite** - Production-ready and development databases
- **JWT Authentication** - Secure token-based authentication with refresh tokens
- **Django CORS Headers** - Cross-origin resource sharing
- **Django Filter** - Advanced filtering capabilities
- **Redis** - Caching and real-time features

### **Frontend (Vue.js 3)**
- **Vue 3** - Progressive JavaScript framework with Composition API
- **Vuetify 3** - Material Design component library
- **Vue Router 4** - Client-side routing with navigation guards
- **Pinia** - State management
- **Axios** - Promise-based HTTP client
- **Vite** - Next-generation build tool
- **ESLint** + **Prettier** - Code quality and formatting

## **🎯 Features**

### **📊 Dashboard & Analytics**
- Real-time sales pipeline visualization
- Deal stage progress tracking
- Activity timeline and notifications
- Performance metrics and KPI tracking
- Interactive charts and statistics

### **👥 Contact Management**
- Complete contact profiles with custom fields
- Contact categorization and tagging
- Relationship tracking and history
- Bulk contact import/export
- Advanced search and filtering

### **🏢 Company Management**
- Company profiles with industry classification
- Team members and stakeholder tracking
- Company hierarchy and relationships
- Revenue and size categorization
- Geographic distribution mapping

### **💰 Deal Pipeline Management**
- Visual sales pipeline with drag-and-drop stages
- Deal value and probability tracking
- Expected close date forecasting
- Deal progress and milestone tracking
- Win/loss analysis

### **✅ Task Management**
- Task prioritization and scheduling
- Recurring task patterns
- Task dependencies and sub-tasks
- Time tracking and estimation
- Overdue task alerts

### **🔒 Security & User Management**
- Role-based access control (RBAC)
- Multi-user workspace
- User activity logging
- Audit trails for all changes
- Secure API authentication

### **📱 UX/UI Features**
- Responsive design (Mobile, Tablet, Desktop)
- Dark/Light theme toggle
- Keyboard shortcuts
- Real-time updates
- Offline capability (PWA ready)
- Progressive Web App features

## **🏗️ Project Architecture**

```
interview/
├── backend/                           # Django Backend
│   ├── crm/                          # Django Project
│   │   ├── settings.py               # Project settings
│   │   ├── urls.py                   # URL routing
│   │   ├── wsgi.py                   # WSGI config
│   │   └── asgi.py                   # ASGI config
│   ├── apps/                         # Django Apps
│   │   ├── users/                    # User management
│   │   │   ├── models.py            # Custom user model
│   │   │   ├── serializers.py       # User serializers
│   │   │   ├── views.py             # API views
│   │   │   └── urls.py              # User URLs
│   │   ├── companies/               # Companies app
│   │   ├── contacts/                # Contacts app
│   │   ├── deals/                   # Deals app
│   │   ├── tasks/                   # Tasks app
│   │   ├── interactions/            # Interactions app
│   │   └── dashboard/               # Dashboard app
│   ├── utils/                        # Shared utilities
│   │   ├── permissions.py           # Custom permissions
│   │   ├── pagination.py            # Custom pagination
│   │   ├── filters.py               # Filter backends
│   │   └── serializers.py           # Base serializers
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   └── db.sqlite3
│
└── frontend/                         # Vue.js Frontend
    ├── src/
    │   ├── assets/                   # Static assets
    │   │   ├── css/
    │   │   │   ├── styles.css       # Global styles
    │   │   │   ├── animations.css   # CSS animations
    │   │   │   └── responsive.css   # Responsive styles
    │   │   └── images/              # Image assets
    │   ├── components/               # Reusable components
    │   │   ├── layout/              # Layout components
    │   │   ├── ui/                  # UI components
    │   │   └── forms/               # Form components
    │   ├── composables/             # Vue composables
    │   │   ├── useApi.js           # API composable
    │   │   ├── useAuth.js          # Auth composable
    │   │   └── useToast.js         # Toast notifications
    │   ├── plugins/                 # Vue plugins
    │   │   └── vuetify.js          # Vuetify configuration
    │   ├── router/                  # Vue Router
    │   │   └── index.js            # Route definitions
    │   ├── services/               # API services
    │   │   ├── api.js              # Axios instance
    │   │   ├── auth.js             # Auth service
    │   │   └── cache.js            # Local storage
    │   ├── stores/                 # Pinia stores
    │   │   ├── auth.js             # Auth store
    │   │   ├── ui.js               # UI store
    │   │   └── notifications.js    # Notifications store
    │   ├── views/                  # Page components
    │   │   ├── DashboardView.vue   # Dashboard page
    │   │   ├── ContactsView.vue    # Contacts page
    │   │   ├── CompaniesView.vue   # Companies page
    │   │   ├── DealsView.vue       # Deals page
    │   │   ├── TasksView.vue       # Tasks page
    │   │   ├── LoginView.vue       # Login page
    │   │   └── ProfileView.vue     # Profile page
    │   ├── App.vue                 # Root component
    │   └── main.js                 # Application entry point
    ├── public/                     # Public assets
    ├── index.html                  # HTML template
    ├── package.json                # Dependencies
    ├── vite.config.js              # Vite configuration
    └── .env.example                # Environment variables
```

## **🚀 Getting Started**

### **Prerequisites**
- Python 3.8+
- Node.js 18+
- PostgreSQL (for production)
- Git

### **Backend Setup**
```bash
# Clone the repository
git clone https://github.com/254Codex/UnityMiniCRM1.git
cd interview/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### **Frontend Setup**
```bash
cd ../frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your API URL

# Run development server
npm run dev
```

### **Docker Setup (Alternative)**
```bash
# Run with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# Admin Panel: http://localhost:8000/admin
```

## **🔐 Authentication**

### **Login Credentials**
- **Demo User:** `demo` / `demo123`
- **Admin User:** `admin` / `admin123` (if created)

### **API Authentication**
- JWT Token-based authentication
- Refresh token support
- Token expiration: 24 hours
- Automatic token refresh

## **📱 API Endpoints**

### **Authentication**
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/refresh/` - Refresh token
- `POST /api/auth/register/` - User registration

### **Dashboard**
- `GET /api/dashboard/stats/` - Overall statistics
- `GET /api/dashboard/pipeline/` - Sales pipeline data
- `GET /api/dashboard/forecast/` - Revenue forecast
- `GET /api/dashboard/activity/` - Recent activity

### **Companies**
- `GET /api/companies/` - List companies (with filters)
- `GET /api/companies/:id/` - Get company details
- `POST /api/companies/` - Create company
- `PUT /api/companies/:id/` - Update company
- `PATCH /api/companies/:id/` - Partial update
- `DELETE /api/companies/:id/` - Soft delete
- `GET /api/companies/:id/contacts/` - Company contacts
- `GET /api/companies/:id/deals/` - Company deals

### **Contacts**
- `GET /api/contacts/` - List contacts (with filters)
- `GET /api/contacts/:id/` - Get contact details
- `POST /api/contacts/` - Create contact
- `PUT /api/contacts/:id/` - Update contact
- `DELETE /api/contacts/:id/` - Soft delete
- `GET /api/contacts/:id/interactions/` - Contact interactions

### **Deals**
- `GET /api/deals/` - List deals (with filters)
- `GET /api/deals/:id/` - Get deal details
- `POST /api/deals/` - Create deal
- `PUT /api/deals/:id/` - Update deal
- `PATCH /api/deals/:id/` - Partial update
- `DELETE /api/deals/:id/` - Soft delete
- `POST /api/deals/:id/change-stage/` - Change deal stage
- `GET /api/deals/:id/tasks/` - Deal tasks

### **Tasks**
- `GET /api/tasks/` - List tasks (with filters)
- `GET /api/tasks/:id/` - Get task details
- `POST /api/tasks/` - Create task
- `PUT /api/tasks/:id/` - Update task
- `DELETE /api/tasks/:id/` - Soft delete
- `POST /api/tasks/:id/complete/` - Mark task complete
- `GET /api/tasks/overdue/` - Overdue tasks
- `GET /api/tasks/upcoming/` - Upcoming tasks

### **Interactions**
- `GET /api/interactions/` - List interactions
- `GET /api/interactions/:id/` - Get interaction details
- `POST /api/interactions/` - Create interaction
- `PUT /api/interactions/:id/` - Update interaction

### **Users**
- `GET /api/users/me/` - Current user profile
- `PUT /api/users/me/` - Update profile
- `GET /api/users/` - List users (for assignment)

## **🎨 Design System**

### **Color Palette**
```css
/* Primary Colors */
--primary-50: #e8eaf6;
--primary-100: #c5cae9;
--primary-200: #9fa8da;
--primary-300: #7986cb;
--primary-400: #5c6bc0;
--primary-500: #3f51b5;   /* Primary Blue */
--primary-600: #3949ab;
--primary-700: #303f9f;
--primary-800: #283593;
--primary-900: #1a237e;   /* Navy Blue */

/* Secondary Colors */
--secondary-500: #0288d1;  /* Lighter Blue */
--accent-500: #39cccc;     /* Teal */
--success-500: #4caf50;
--warning-500: #ff9800;
--error-500: #f44336;
--grey-50: #fafafa;
--grey-100: #f5f5f5;
--grey-900: #212121;
```

### **Typography**
- **Primary Font:** 'Roboto', sans-serif
- **Monospace:** 'Roboto Mono', monospace
- **Base Font Size:** 16px
- **Line Height:** 1.5

### **Breakpoints**
- **Mobile:** < 600px
- **Tablet:** 600px - 960px
- **Desktop:** 960px - 1264px
- **Large Desktop:** > 1264px

## **🛠️ Development**

### **Code Standards**
```bash
# Backend (Python)
black .                     # Code formatting
flake8 .                    # Linting
pytest                      # Testing

# Frontend (JavaScript)
npm run lint                # ESLint
npm run format              # Prettier
npm run test:unit           # Unit tests
```

### **Database Models**

#### **Company**
```python
class Company(models.Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=255)
    industry = CharField(choices=INDUSTRY_CHOICES)
    company_size = CharField(choices=COMPANY_SIZE_CHOICES)
    website = URLField()
    phone = CharField(max_length=50)
    email = EmailField()
    address = TextField()
    city = CharField(max_length=100)
    state = CharField(max_length=100)
    country = CharField(max_length=100)
    postal_code = CharField(max_length=20)
    notes = TextField(blank=True)
    tags = CharField(max_length=500)  # Comma-separated
    annual_revenue = DecimalField(max_digits=12, decimal_places=2)
    founded_year = IntegerField()
    assigned_to = ForeignKey(User, related_name='assigned_companies')
    created_by = ForeignKey(User, related_name='created_companies')
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

#### **Contact**
```python
class Contact(models.Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    salutation = CharField(choices=SALUTATION_CHOICES)
    first_name = CharField(max_length=100)
    last_name = CharField(max_length=100)
    email = EmailField()
    phone = CharField(max_length=50)
    mobile = CharField(max_length=50, blank=True)
    position = CharField(max_length=200)
    department = CharField(max_length=200, blank=True)
    company = ForeignKey(Company, on_delete=models.CASCADE, related_name='contacts')
    source = CharField(choices=CONTACT_SOURCE_CHOICES)
    is_decision_maker = BooleanField(default=False)
    date_of_birth = DateField(null=True, blank=True)
    notes = TextField(blank=True)
    tags = CharField(max_length=500)  # Comma-separated
    social_linkedin = URLField(blank=True)
    social_twitter = URLField(blank=True)
    assigned_to = ForeignKey(User, related_name='assigned_contacts')
    created_by = ForeignKey(User, related_name='created_contacts')
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

#### **Deal**
```python
class Deal(models.Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deal_code = CharField(max_length=50, unique=True, editable=False)
    title = CharField(max_length=255)
    amount = DecimalField(max_digits=12, decimal_places=2)
    currency = CharField(choices=CURRENCY_CHOICES, default='USD')
    stage = CharField(choices=DEAL_STAGE_CHOICES, default='lead')
    probability = IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    expected_close_date = DateField(null=True, blank=True)
    company = ForeignKey(Company, on_delete=models.CASCADE, related_name='deals')
    contact = ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals')
    notes = TextField(blank=True)
    tags = CharField(max_length=500)  # Comma-separated
    assigned_to = ForeignKey(User, related_name='assigned_deals')
    team_members = ManyToManyField(User, related_name='team_deals', blank=True)
    status = CharField(choices=DEAL_STATUS_CHOICES, default='active')
    created_by = ForeignKey(User, related_name='created_deals')
    closed_at = DateTimeField(null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## **📊 Performance Optimization**

### **Backend**
- Database query optimization with `select_related` and `prefetch_related`
- Redis caching for frequently accessed data
- Pagination for large datasets
- Database indexing for common queries
- Gzip compression for API responses

### **Frontend**
- Code splitting and lazy loading
- Component-level caching
- Image optimization and lazy loading
- Service worker for offline caching
- Bundle size optimization

## **🔒 Security**

### **Implemented Security Features**
- JWT authentication with refresh tokens
- CSRF protection
- XSS prevention
- SQL injection prevention
- Rate limiting
- CORS configuration
- HTTPS enforcement (production)
- Secure password hashing (bcrypt)
- Session management

### **Data Protection**
- GDPR compliance ready
- Data encryption at rest
- Audit logging for all data changes
- User data export functionality
- Right to be forgotten implementation

## **🤝 Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## **📄 License**

This project is created for demonstration and interview purposes.

## **📞 Support**

For support, email example@example.com or create an issue in the GitHub repository.

---

**Built with ❤️ using Django, Vue.js, and Vuetify**
