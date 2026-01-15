// frontend/src/services/api.js

import axios from 'axios';
import store from '@/store'; // If you're using Vuex
import router from '@/router';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/', // Adjust based on your backend URL
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Handle specific HTTP status codes
      switch (error.response.status) {
        case 401:
          // Unauthorized - redirect to login
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          router.push('/login');
          break;
        case 403:
          // Forbidden - show access denied message
          console.error('Access denied:', error.response.data);
          break;
        case 404:
          // Not found
          console.error('Resource not found:', error.response.config.url);
          break;
        case 500:
          // Server error
          console.error('Server error:', error.response.data);
          break;
      }
    }
    return Promise.reject(error);
  }
);

// Helper function to handle UUID validation
const validateUUID = (id) => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(id);
};

// API Services
export default {
  // ==================== AUTHENTICATION ====================
  auth: {
    login(credentials) {
      return apiClient.post('login/', credentials);
    },
    logout() {
      return apiClient.post('logout/');
    },
    register(userData) {
      return apiClient.post('register/', userData);
    },
    getCurrentUser() {
      return apiClient.get('users/me/');
    },
    changePassword(passwords) {
      return apiClient.post('change-password/', passwords);
    },
  },

  // ==================== DASHBOARD ====================
  dashboard: {
    getStats() {
      return apiClient.get('dashboard/stats/');
    },
    getPipeline() {
      return apiClient.get('deals/pipeline/');
    },
    getForecast() {
      return apiClient.get('deals/forecast/');
    },
    getRecentActivity() {
      return apiClient.get('activity/recent/');
    },
  },

  // ==================== COMPANIES ====================
  companies: {
    // Get all companies with optional filters
    getAll(params = {}) {
      const config = { params };
      return apiClient.get('companies/', config);
    },
    
    // Get a single company by UUID
    get(id) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.get(`companies/${id}/`);
    },
    
    // Create a new company
    create(companyData) {
      // Prepare data for new enhanced model
      const enhancedData = {
        name: companyData.name,
        industry: companyData.industry || 'other',
        company_size: companyData.company_size || null,
        website: companyData.website || '',
        phone: companyData.phone || '',
        email: companyData.email || '',
        address: companyData.address || '',
        city: companyData.city || '',
        state: companyData.state || '',
        country: companyData.country || '',
        postal_code: companyData.postal_code || '',
        notes: companyData.notes || '',
        tags: companyData.tags ? companyData.tags.join(',') : '',
        annual_revenue: companyData.annual_revenue || null,
        founded_year: companyData.founded_year || null,
        assigned_to: companyData.assigned_to || null,
      };
      return apiClient.post('companies/', enhancedData);
    },
    
    // Update an existing company
    update(id, companyData) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.put(`companies/${id}/`, companyData);
    },
    
    // Partial update (PATCH)
    partialUpdate(id, companyData) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.patch(`companies/${id}/`, companyData);
    },
    
    // Delete (soft delete) a company
    delete(id) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.delete(`companies/${id}/`);
    },
    
    // Get company contacts
    getContacts(companyId) {
      if (!validateUUID(companyId)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.get(`companies/${companyId}/contacts/`);
    },
    
    // Get company deals
    getDeals(companyId) {
      if (!validateUUID(companyId)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.get(`companies/${companyId}/deals/`);
    },
    
    // Get company statistics
    getStats(companyId) {
      if (!validateUUID(companyId)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.get(`companies/${companyId}/stats/`);
    },
    
    // Get list of industries with counts
    getIndustries() {
      return apiClient.get('companies/industries/');
    },
    
    // Bulk operations
    bulkDelete(ids) {
      return apiClient.post('bulk-delete/', {
        model_type: 'company',
        ids: ids,
      });
    },
    
    // Export companies
    export(format = 'json', filters = {}) {
      const params = { model_type: 'companies', format, ...filters };
      return apiClient.get('export/', { params, responseType: 'blob' });
    },
  },

  // ==================== CONTACTS ====================
  contacts: {
    // Get all contacts with optional filters
    getAll(params = {}) {
      const config = { params };
      return apiClient.get('contacts/', config);
    },
    
    // Get a single contact by UUID
    get(id) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.get(`contacts/${id}/`);
    },
    
    // Create a new contact
    create(contactData) {
      // Prepare data for new enhanced model
      const enhancedData = {
        salutation: contactData.salutation || '',
        first_name: contactData.first_name,
        last_name: contactData.last_name,
        email: contactData.email,
        phone: contactData.phone || '',
        mobile: contactData.mobile || '',
        position: contactData.position || '',
        department: contactData.department || '',
        company: contactData.company || null,
        source: contactData.source || 'other',
        is_decision_maker: contactData.is_decision_maker || false,
        date_of_birth: contactData.date_of_birth || null,
        notes: contactData.notes || '',
        tags: contactData.tags ? contactData.tags.join(',') : '',
        social_linkedin: contactData.social_linkedin || '',
        social_twitter: contactData.social_twitter || '',
        assigned_to: contactData.assigned_to || null,
      };
      return apiClient.post('contacts/', enhancedData);
    },
    
    // Update an existing contact
    update(id, contactData) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.put(`contacts/${id}/`, contactData);
    },
    
    // Partial update (PATCH)
    partialUpdate(id, contactData) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.patch(`contacts/${id}/`, contactData);
    },
    
    // Delete (soft delete) a contact
    delete(id) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.delete(`contacts/${id}/`);
    },
    
    // Get contact interactions
    getInteractions(contactId) {
      if (!validateUUID(contactId)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.get(`contacts/${contactId}/interactions/`);
    },
    
    // Get contact tasks
    getTasks(contactId) {
      if (!validateUUID(contactId)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.get(`contacts/${contactId}/tasks/`);
    },
    
    // Get list of contact sources with counts
    getSources() {
      return apiClient.get('contacts/sources/');
    },
    
    // Create interaction for contact
    createInteraction(contactId, interactionData) {
      if (!validateUUID(contactId)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.post(`contacts/${contactId}/interactions/`, interactionData);
    },
    
    // Bulk operations
    bulkDelete(ids) {
      return apiClient.post('bulk-delete/', {
        model_type: 'contact',
        ids: ids,
      });
    },
  },

  // ==================== DEALS ====================
  deals: {
    // Get all deals with optional filters
    getAll(params = {}) {
      const config = { params };
      return apiClient.get('deals/', config);
    },
    
    // Get a single deal by UUID
    get(id) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.get(`deals/${id}/`);
    },
    
    // Create a new deal
    create(dealData) {
      // Note: deal_code is auto-generated by backend
      const enhancedData = {
        title: dealData.title,
        amount: dealData.amount,
        currency: dealData.currency || 'USD',
        stage: dealData.stage || 'lead',
        probability: dealData.probability || 0,
        expected_close_date: dealData.expected_close_date || null,
        company: dealData.company, // Required
        contact: dealData.contact || null,
        notes: dealData.notes || '',
        tags: dealData.tags ? dealData.tags.join(',') : '',
        assigned_to: dealData.assigned_to || null,
        team_members: dealData.team_members || [],
      };
      return apiClient.post('deals/', enhancedData);
    },
    
    // Update an existing deal
    update(id, dealData) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.put(`deals/${id}/`, dealData);
    },
    
    // Partial update (PATCH)
    partialUpdate(id, dealData) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.patch(`deals/${id}/`, dealData);
    },
    
    // Delete (soft delete) a deal
    delete(id) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.delete(`deals/${id}/`);
    },
    
    // Change deal stage
    changeStage(dealId, stageData) {
      if (!validateUUID(dealId)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.post(`deals/${dealId}/change_stage/`, stageData);
    },
    
    // Get deal stage history
    getStageHistory(dealId) {
      if (!validateUUID(dealId)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.get(`deals/${dealId}/stage_history/`);
    },
    
    // Get deal tasks
    getTasks(dealId) {
      if (!validateUUID(dealId)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.get(`deals/${dealId}/tasks/`);
    },
    
    // Get deal pipeline statistics
    getPipeline() {
      return apiClient.get('deals/pipeline/');
    },
    
    // Get sales forecast
    getForecast() {
      return apiClient.get('deals/forecast/');
    },
    
    // Close a deal (won or lost)
    closeDeal(dealId, closeData) {
      if (!validateUUID(dealId)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.post(`deals/${dealId}/close/`, closeData);
    },
    
    // Bulk operations
    bulkDelete(ids) {
      return apiClient.post('bulk-delete/', {
        model_type: 'deal',
        ids: ids,
      });
    },
  },

  // ==================== TASKS ====================
  tasks: {
    // Get all tasks with optional filters
    getAll(params = {}) {
      const config = { params };
      return apiClient.get('tasks/', config);
    },
    
    // Get a single task by UUID
    get(id) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.get(`tasks/${id}/`);
    },
    
    // Create a new task
    create(taskData) {
      const enhancedData = {
        title: taskData.title,
        description: taskData.description || '',
        task_type: taskData.task_type || 'other',
        status: taskData.status || 'pending',
        priority: taskData.priority || 'medium',
        due_date: taskData.due_date || null,
        estimated_hours: taskData.estimated_hours || null,
        contact: taskData.contact || null,
        deal: taskData.deal || null,
        company: taskData.company || null,
        assigned_to: taskData.assigned_to || null,
        recurrence_pattern: taskData.recurrence_pattern || '',
        parent_task: taskData.parent_task || null,
        tags: taskData.tags ? taskData.tags.join(',') : '',
      };
      return apiClient.post('tasks/', enhancedData);
    },
    
    // Update an existing task
    update(id, taskData) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.put(`tasks/${id}/`, taskData);
    },
    
    // Partial update (PATCH)
    partialUpdate(id, taskData) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.patch(`tasks/${id}/`, taskData);
    },
    
    // Delete (soft delete) a task
    delete(id) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.delete(`tasks/${id}/`);
    },
    
    // Complete a task
    complete(id, completionData) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.post(`tasks/${id}/complete/`, completionData);
    },
    
    // Reassign a task
    reassign(id, reassignData) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.post(`tasks/${id}/reassign/`, reassignData);
    },
    
    // Get overdue tasks
    getOverdue() {
      return apiClient.get('tasks/overdue/');
    },
    
    // Get upcoming tasks (next 7 days)
    getUpcoming() {
      return apiClient.get('tasks/upcoming/');
    },
    
    // Get tasks assigned to current user
    getMyTasks() {
      return apiClient.get('tasks/my_tasks/');
    },
    
    // Get task subtasks
    getSubtasks(taskId) {
      if (!validateUUID(taskId)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.get(`tasks/${taskId}/subtasks/`);
    },
    
    // Bulk operations
    bulkDelete(ids) {
      return apiClient.post('bulk-delete/', {
        model_type: 'task',
        ids: ids,
      });
    },
  },

  // ==================== INTERACTIONS ====================
  interactions: {
    // Get all interactions
    getAll(params = {}) {
      const config = { params };
      return apiClient.get('interactions/', config);
    },
    
    // Get a single interaction by UUID
    get(id) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.get(`interactions/${id}/`);
    },
    
    // Create a new interaction
    create(interactionData) {
      return apiClient.post('interactions/', interactionData);
    },
    
    // Update an interaction
    update(id, interactionData) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.put(`interactions/${id}/`, interactionData);
    },
    
    // Delete an interaction
    delete(id) {
      if (!validateUUID(id)) {
        return Promise.reject(new Error('Invalid UUID format'));
      }
      return apiClient.delete(`interactions/${id}/`);
    },
  },

  // ==================== USERS & PROFILES ====================
  users: {
    // Get current user profile
    getProfile() {
      return apiClient.get('profile/');
    },
    
    // Update user profile
    updateProfile(profileData) {
      // Handle avatar upload separately if it's a file
      if (profileData.avatar instanceof File) {
        const formData = new FormData();
        formData.append('avatar', profileData.avatar);
        
        // Add other fields
        Object.keys(profileData).forEach(key => {
          if (key !== 'avatar' && profileData[key] !== undefined) {
            formData.append(key, profileData[key]);
          }
        });
        
        return apiClient.put('profile/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      }
      
      return apiClient.put('profile/', profileData);
    },
    
    // Get all users (for assignment dropdowns)
    getAll() {
      return apiClient.get('users/');
    },
    
    // Get notification preferences
    getNotificationPreferences() {
      return apiClient.get('notification-preferences/');
    },
    
    // Update notification preferences
    updateNotificationPreferences(preferences) {
      return apiClient.put('notification-preferences/', preferences);
    },
  },

  // ==================== UTILITIES ====================
  utils: {
    // Get choices/options for dropdowns
    getChoices() {
      return apiClient.get('choices/');
    },
    
    // Upload file
    uploadFile(file, entityType, entityId) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('entity_type', entityType);
      formData.append('entity_id', entityId);
      
      return apiClient.post('upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    },
    
    // Search across all entities
    search(query) {
      return apiClient.get('search/', { params: { q: query } });
    },
  },

  // ==================== CONSTANTS ====================
  constants: {
    // Industry choices
    INDUSTRY_CHOICES: [
      { value: 'technology', label: 'Technology' },
      { value: 'finance', label: 'Finance' },
      { value: 'healthcare', label: 'Healthcare' },
      { value: 'education', label: 'Education' },
      { value: 'retail', label: 'Retail' },
      { value: 'manufacturing', label: 'Manufacturing' },
      { value: 'consulting', label: 'Consulting' },
      { value: 'other', label: 'Other' },
    ],
    
    // Company size choices
    COMPANY_SIZE_CHOICES: [
      { value: 'micro', label: 'Micro (1-9)' },
      { value: 'small', label: 'Small (10-49)' },
      { value: 'medium', label: 'Medium (50-249)' },
      { value: 'large', label: 'Large (250+)' },
    ],
    
    // Contact salutation choices
    SALUTATION_CHOICES: [
      { value: 'mr', label: 'Mr.' },
      { value: 'mrs', label: 'Mrs.' },
      { value: 'ms', label: 'Ms.' },
      { value: 'dr', label: 'Dr.' },
      { value: 'prof', label: 'Prof.' },
    ],
    
    // Contact source choices
    CONTACT_SOURCE_CHOICES: [
      { value: 'website', label: 'Website' },
      { value: 'referral', label: 'Referral' },
      { value: 'conference', label: 'Conference' },
      { value: 'social', label: 'Social Media' },
      { value: 'cold_call', label: 'Cold Call' },
      { value: 'other', label: 'Other' },
    ],
    
    // Deal stage choices
    DEAL_STAGE_CHOICES: [
      { value: 'lead', label: 'Lead' },
      { value: 'qualified', label: 'Qualified' },
      { value: 'proposal', label: 'Proposal' },
      { value: 'negotiation', label: 'Negotiation' },
      { value: 'closed_won', label: 'Closed Won' },
      { value: 'closed_lost', label: 'Closed Lost' },
      { value: 'on_hold', label: 'On Hold' },
    ],
    
    // Deal currency choices
    CURRENCY_CHOICES: [
      { value: 'USD', label: 'US Dollar' },
      { value: 'EUR', label: 'Euro' },
      { value: 'GBP', label: 'British Pound' },
      { value: 'JPY', label: 'Japanese Yen' },
      { value: 'CAD', label: 'Canadian Dollar' },
    ],
    
    // Task type choices
    TASK_TYPE_CHOICES: [
      { value: 'call', label: 'Phone Call' },
      { value: 'email', label: 'Email' },
      { value: 'meeting', label: 'Meeting' },
      { value: 'follow_up', label: 'Follow Up' },
      { value: 'document', label: 'Document' },
      { value: 'other', label: 'Other' },
    ],
    
    // Task status choices
    TASK_STATUS_CHOICES: [
      { value: 'pending', label: 'Pending' },
      { value: 'in_progress', label: 'In Progress' },
      { value: 'completed', label: 'Completed' },
      { value: 'cancelled', label: 'Cancelled' },
      { value: 'deferred', label: 'Deferred' },
    ],
    
    // Task priority choices
    TASK_PRIORITY_CHOICES: [
      { value: 'low', label: 'Low' },
      { value: 'medium', label: 'Medium' },
      { value: 'high', label: 'High' },
      { value: 'urgent', label: 'Urgent' },
    ],
    
    // Interaction type choices
    INTERACTION_TYPE_CHOICES: [
      { value: 'call', label: 'Phone Call' },
      { value: 'email', label: 'Email' },
      { value: 'meeting', label: 'Meeting' },
      { value: 'note', label: 'Note' },
      { value: 'demo', label: 'Product Demo' },
      { value: 'proposal', label: 'Proposal Sent' },
    ],
  },
};
