from django.contrib import admin
from .models import Company, Contact, Deal, Task


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'industry', 'email', 'phone', 'created_at']
    list_filter = ['industry', 'created_at']
    search_fields = ['name', 'email', 'industry']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'company', 'position', 'created_at']
    list_filter = ['company', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'amount', 'stage', 'probability', 'expected_close_date', 'created_at']
    list_filter = ['stage', 'created_at']
    search_fields = ['title', 'company__name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'due_date', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description']
