# backend/tasks/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import (
    Company, Contact, Deal, Task,
    Interaction, DealStageHistory, NotificationPreference
)


# Inline admins for related models
class ContactInline(admin.TabularInline):
    model = Contact
    extra = 0
    fields = ['full_name', 'email', 'phone', 'position', 'is_decision_maker', 'is_active']
    readonly_fields = ['full_name']
    show_change_link = True
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Name'


class DealInline(admin.TabularInline):
    model = Deal
    extra = 0
    fields = ['deal_code', 'title', 'amount', 'stage', 'probability', 'expected_close_date', 'is_active']
    readonly_fields = ['deal_code']
    show_change_link = True


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ['title', 'task_type', 'priority', 'status', 'due_date', 'assigned_to', 'is_active']
    show_change_link = True


class InteractionInline(admin.TabularInline):
    model = Interaction
    extra = 0
    fields = ['interaction_type', 'subject', 'interaction_date', 'duration_minutes', 'created_by']
    readonly_fields = ['created_by']
    show_change_link = True


class DealStageHistoryInline(admin.TabularInline):
    model = DealStageHistory
    extra = 0
    fields = ['from_stage', 'to_stage', 'changed_at', 'changed_by', 'notes']
    readonly_fields = ['from_stage', 'to_stage', 'changed_at', 'changed_by']
    can_delete = False
    max_num = 10


# Custom filters
class ActiveFilter(admin.SimpleListFilter):
    title = 'active status'
    parameter_name = 'is_active'
    
    def lookups(self, request, model_admin):
        return (
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True)
        if self.value() == 'inactive':
            return queryset.filter(is_active=False)


class OverdueTaskFilter(admin.SimpleListFilter):
    title = 'overdue status'
    parameter_name = 'overdue'
    
    def lookups(self, request, model_admin):
        return (
            ('overdue', 'Overdue'),
            ('not_overdue', 'Not Overdue'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'overdue':
            return queryset.filter(
                due_date__lt=timezone.now(),
                status__in=['pending', 'in_progress']
            )
        if self.value() == 'not_overdue':
            return queryset.exclude(
                due_date__lt=timezone.now(),
                status__in=['pending', 'in_progress']
            )


class RecentActivityFilter(admin.SimpleListFilter):
    title = 'recent activity'
    parameter_name = 'recent'
    
    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('week', 'Last 7 days'),
            ('month', 'Last 30 days'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'today':
            return queryset.filter(created_at__date=timezone.now().date())
        if self.value() == 'week':
            return queryset.filter(created_at__gte=timezone.now() - timedelta(days=7))
        if self.value() == 'month':
            return queryset.filter(created_at__gte=timezone.now() - timedelta(days=30))


# Model admins
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'industry_display', 'company_size_display', 
        'email', 'phone', 'contact_count', 'deal_count',
        'is_active', 'created_at', 'view_contacts_link'
    ]
    list_filter = [
        ActiveFilter, 'industry', 'company_size',
        RecentActivityFilter, 'created_by', 'assigned_to'
    ]
    search_fields = [
        'name', 'industry', 'email', 'phone', 
        'address', 'city', 'state', 'country', 'tags'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'deleted_at',
        'contact_count', 'active_deals_count', 'total_deal_value'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id', 'name', 'industry', 'company_size',
                'website', 'email', 'phone'
            )
        }),
        ('Location', {
            'fields': (
                'address', 'city', 'state', 'country', 'postal_code'
            )
        }),
        ('Financial Information', {
            'fields': (
                'annual_revenue', 'founded_year',
                'total_deal_value', 'active_deals_count'
            )
        }),
        ('Additional Information', {
            'fields': (
                'notes', 'tags'
            )
        }),
        ('Team Assignment', {
            'fields': (
                'created_by', 'assigned_to'
            )
        }),
        ('Status & Statistics', {
            'fields': (
                'contact_count', 'is_active', 'deleted_at'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    inlines = [ContactInline, DealInline]
    actions = ['activate_companies', 'deactivate_companies', 'export_companies']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    def industry_display(self, obj):
        return obj.get_industry_display()
    industry_display.short_description = 'Industry'
    industry_display.admin_order_field = 'industry'
    
    def company_size_display(self, obj):
        return obj.get_company_size_display() if obj.company_size else '-'
    company_size_display.short_description = 'Size'
    company_size_display.admin_order_field = 'company_size'
    
    def contact_count(self, obj):
        return obj.contacts.filter(is_active=True).count()
    contact_count.short_description = 'Contacts'
    
    def deal_count(self, obj):
        return obj.deals.filter(is_active=True).count()
    deal_count.short_description = 'Deals'
    
    def active_deals_count(self, obj):
        from django.db.models import Q
        return obj.deals.filter(
            is_active=True
        ).exclude(
            Q(stage='closed_won') | Q(stage='closed_lost')
        ).count()
    active_deals_count.short_description = 'Active Deals'
    
    def view_contacts_link(self, obj):
        url = reverse('admin:tasks_contact_changelist') + f'?company__id__exact={obj.id}'
        count = obj.contacts.filter(is_active=True).count()
        return format_html(
            '<a href="{}">{} Contact{}</a>',
            url, count, 's' if count != 1 else ''
        )
    view_contacts_link.short_description = 'Contacts'
    
    def activate_companies(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} companies activated.')
    activate_companies.short_description = 'Activate selected companies'
    
    def deactivate_companies(self, request, queryset):
        updated = queryset.update(is_active=False, deleted_at=timezone.now())
        self.message_user(request, f'{updated} companies deactivated.')
    deactivate_companies.short_description = 'Deactivate selected companies'
    
    def export_companies(self, request, queryset):
        # This would typically export to CSV or Excel
        self.message_user(request, f'Export functionality for {queryset.count()} companies.')
    export_companies.short_description = 'Export selected companies'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'email', 'phone', 'company_link',
        'position', 'is_decision_maker', 'source_display',
        'interaction_count', 'is_active', 'created_at'
    ]
    list_filter = [
        ActiveFilter, 'source', 'is_decision_maker', 
        'company', 'assigned_to', RecentActivityFilter
    ]
    search_fields = [
        'first_name', 'last_name', 'email', 'phone', 'mobile',
        'position', 'department', 'company__name', 'tags'
    ]
    readonly_fields = [
        'id', 'full_name', 'age', 'created_at', 'updated_at', 'deleted_at',
        'interaction_count', 'task_count'
    ]
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'id', 'salutation', 'first_name', 'last_name', 'full_name',
                'email', 'phone', 'mobile', 'date_of_birth', 'age'
            )
        }),
        ('Professional Information', {
            'fields': (
                'position', 'department', 'company',
                'is_decision_maker', 'source'
            )
        }),
        ('Social & Contact Information', {
            'fields': (
                'social_linkedin', 'social_twitter',
                'notes', 'tags'
            )
        }),
        ('Team Assignment', {
            'fields': (
                'created_by', 'assigned_to'
            )
        }),
        ('Statistics', {
            'fields': (
                'interaction_count', 'task_count'
            )
        }),
        ('Status', {
            'fields': (
                'is_active', 'deleted_at'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    inlines = [InteractionInline]
    actions = ['mark_as_decision_maker', 'export_contacts']
    date_hierarchy = 'created_at'
    list_select_related = ['company']
    list_per_page = 25
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Name'
    full_name.admin_order_field = 'last_name'
    
    def source_display(self, obj):
        return obj.get_source_display()
    source_display.short_description = 'Source'
    source_display.admin_order_field = 'source'
    
    def company_link(self, obj):
        if obj.company:
            url = reverse('admin:tasks_company_change', args=[obj.company.id])
            return format_html('<a href="{}">{}</a>', url, obj.company.name)
        return '-'
    company_link.short_description = 'Company'
    company_link.admin_order_field = 'company__name'
    
    def interaction_count(self, obj):
        return obj.interactions.filter(is_active=True).count()
    interaction_count.short_description = 'Interactions'
    
    def task_count(self, obj):
        return obj.tasks.filter(is_active=True).count()
    task_count.short_description = 'Tasks'
    
    def age(self, obj):
        return obj.age
    age.short_description = 'Age'
    
    def mark_as_decision_maker(self, request, queryset):
        updated = queryset.update(is_decision_maker=True)
        self.message_user(request, f'{updated} contacts marked as decision makers.')
    mark_as_decision_maker.short_description = 'Mark as decision maker'


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = [
        'deal_code', 'title', 'company_link', 'contact_link',
        'amount_display', 'stage_display', 'probability_bar',
        'expected_close_date', 'days_until_close', 'is_active', 'created_at'
    ]
    list_filter = [
        ActiveFilter, 'stage', 'currency', 'forecast_category',
        'company', 'assigned_to', 'expected_close_date'
    ]
    search_fields = [
        'deal_code', 'title', 'company__name', 
        'contact__first_name', 'contact__last_name', 'tags'
    ]
    readonly_fields = [
        'id', 'deal_code', 'created_at', 'updated_at', 'deleted_at',
        'weighted_amount', 'days_in_stage', 'is_closed',
        'stage_history_link'
    ]
    fieldsets = (
        ('Deal Information', {
            'fields': (
                'id', 'deal_code', 'title', 'amount', 'currency',
                'stage', 'probability', 'weighted_amount'
            )
        }),
        ('Parties', {
            'fields': (
                'company', 'contact'
            )
        }),
        ('Timeline', {
            'fields': (
                'expected_close_date', 'actual_close_date',
                'last_contact_date', 'next_follow_up',
                'days_in_stage', 'is_closed'
            )
        }),
        ('Team', {
            'fields': (
                'created_by', 'assigned_to', 'team_members'
            )
        }),
        ('Forecasting', {
            'fields': (
                'forecast_category', 'lost_reason', 'lost_notes'
            )
        }),
        ('Additional Information', {
            'fields': (
                'notes', 'tags'
            )
        }),
        ('Status', {
            'fields': (
                'is_active', 'deleted_at'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    inlines = [TaskInline, DealStageHistoryInline]
    actions = ['change_stage', 'close_deals', 'export_deals']
    filter_horizontal = ['team_members']
    date_hierarchy = 'expected_close_date'
    list_per_page = 25
    
    def amount_display(self, obj):
        return f"{obj.currency} {obj.amount:,.2f}"
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def stage_display(self, obj):
        return obj.get_stage_display()
    stage_display.short_description = 'Stage'
    stage_display.admin_order_field = 'stage'
    
    def probability_bar(self, obj):
        color = 'green' if obj.probability >= 70 else 'orange' if obj.probability >= 40 else 'red'
        return format_html(
            '<div style="width: 100px; background: #eee; border-radius: 3px;">'
            '<div style="width: {}px; height: 20px; background: {}; border-radius: 3px; text-align: center; color: white; line-height: 20px;">'
            '{}%'
            '</div>'
            '</div>',
            obj.probability, color, obj.probability
        )
    probability_bar.short_description = 'Probability'
    
    def company_link(self, obj):
        if obj.company:
            url = reverse('admin:tasks_company_change', args=[obj.company.id])
            return format_html('<a href="{}">{}</a>', url, obj.company.name)
        return '-'
    company_link.short_description = 'Company'
    company_link.admin_order_field = 'company__name'
    
    def contact_link(self, obj):
        if obj.contact:
            url = reverse('admin:tasks_contact_change', args=[obj.contact.id])
            return format_html('<a href="{}">{}</a>', url, obj.contact.full_name)
        return '-'
    contact_link.short_description = 'Contact'
    contact_link.admin_order_field = 'contact__last_name'
    
    def days_until_close(self, obj):
        if obj.expected_close_date:
            delta = obj.expected_close_date - timezone.now().date()
            days = delta.days
            if days > 0:
                return f"In {days} days"
            elif days < 0:
                return f"{abs(days)} days ago"
            else:
                return "Today"
        return '-'
    days_until_close.short_description = 'Close Date'
    
    def weighted_amount(self, obj):
        return obj.weighted_amount
    weighted_amount.short_description = 'Weighted Amount'
    
    def stage_history_link(self, obj):
        count = obj.stage_history.count()
        if count > 0:
            url = reverse('admin:tasks_dealstagehistory_changelist') + f'?deal__id__exact={obj.id}'
            return format_html('<a href="{}">View {} stage change{}</a>', url, count, 's' if count != 1 else '')
        return 'No stage changes'
    stage_history_link.short_description = 'Stage History'
    
    def change_stage(self, request, queryset):
        # This would typically show a custom form to select new stage
        self.message_user(request, f'Stage change functionality for {queryset.count()} deals.')
    change_stage.short_description = 'Change stage for selected deals'
    
    def close_deals(self, request, queryset):
        # This would close deals (won/lost)
        self.message_user(request, f'Close functionality for {queryset.count()} deals.')
    close_deals.short_description = 'Close selected deals'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'task_type_display', 'priority_display',
        'status_display', 'due_date', 'overdue_indicator',
        'assigned_to_link', 'related_entity_link', 'is_active'
    ]
    list_filter = [
        ActiveFilter, OverdueTaskFilter, 'task_type', 
        'status', 'priority', 'assigned_to', 'due_date'
    ]
    search_fields = [
        'title', 'description', 'contact__first_name',
        'contact__last_name', 'deal__title', 'company__name', 'tags'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'deleted_at',
        'is_overdue', 'days_overdue', 'completion_rate',
        'subtasks_count'
    ]
    fieldsets = (
        ('Task Details', {
            'fields': (
                'id', 'title', 'description', 'task_type',
                'status', 'priority'
            )
        }),
        ('Timing', {
            'fields': (
                'due_date', 'completed_date', 
                'is_overdue', 'days_overdue',
                'estimated_hours', 'actual_hours', 'completion_rate'
            )
        }),
        ('Relationships', {
            'fields': (
                'contact', 'deal', 'company', 'parent_task'
            )
        }),
        ('Assignment', {
            'fields': (
                'created_by', 'assigned_to'
            )
        }),
        ('Additional Information', {
            'fields': (
                'recurrence_pattern', 'tags', 'attachment'
            )
        }),
        ('Subtasks', {
            'fields': (
                'subtasks_count',
            )
        }),
        ('Status', {
            'fields': (
                'is_active', 'deleted_at'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_completed', 'reassign_tasks', 'export_tasks']
    date_hierarchy = 'due_date'
    list_per_page = 25
    
    def task_type_display(self, obj):
        return obj.get_task_type_display()
    task_type_display.short_description = 'Type'
    task_type_display.admin_order_field = 'task_type'
    
    def priority_display(self, obj):
        color_map = {
            'low': 'gray',
            'medium': 'blue',
            'high': 'orange',
            'urgent': 'red'
        }
        color = color_map.get(obj.priority, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_priority_display()
        )
    priority_display.short_description = 'Priority'
    priority_display.admin_order_field = 'priority'
    
    def status_display(self, obj):
        color_map = {
            'pending': 'orange',
            'in_progress': 'blue',
            'completed': 'green',
            'cancelled': 'red',
            'deferred': 'gray'
        }
        color = color_map.get(obj.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def overdue_indicator(self, obj):
        if obj.is_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ OVERDUE ({} days)</span>',
                obj.days_overdue
            )
        elif obj.due_date:
            days = (obj.due_date.date() - timezone.now().date()).days
            if days <= 3:
                return format_html(
                    '<span style="color: orange;">Due in {} days</span>',
                    days
                )
        return '-'
    overdue_indicator.short_description = 'Due Status'
    
    def assigned_to_link(self, obj):
        if obj.assigned_to:
            url = reverse('admin:auth_user_change', args=[obj.assigned_to.id])
            return format_html('<a href="{}">{}</a>', url, obj.assigned_to.get_full_name() or obj.assigned_to.username)
        return '-'
    assigned_to_link.short_description = 'Assigned To'
    
    def related_entity_link(self, obj):
        if obj.contact:
            url = reverse('admin:tasks_contact_change', args=[obj.contact.id])
            return format_html('<a href="{}">👤 {}</a>', url, obj.contact.full_name)
        elif obj.deal:
            url = reverse('admin:tasks_deal_change', args=[obj.deal.id])
            return format_html('<a href="{}">💰 {}</a>', url, obj.deal.title)
        elif obj.company:
            url = reverse('admin:tasks_company_change', args=[obj.company.id])
            return format_html('<a href="{}">🏢 {}</a>', url, obj.company.name)
        return '-'
    related_entity_link.short_description = 'Related To'
    
    def subtasks_count(self, obj):
        count = obj.subtasks.count()
        if count > 0:
            url = reverse('admin:tasks_task_changelist') + f'?parent_task__id__exact={obj.id}'
            return format_html('<a href="{}">{} subtask{}</a>', url, count, 's' if count != 1 else '')
        return 'No subtasks'
    subtasks_count.short_description = 'Subtasks'
    
    def mark_completed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status='completed',
            completed_date=timezone.now()
        )
        self.message_user(request, f'{updated} tasks marked as completed.')
    mark_completed.short_description = 'Mark selected tasks as completed'


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = [
        'subject', 'interaction_type_display',
        'contact_link', 'company_link', 'deal_link',
        'interaction_date', 'duration_minutes',
        'requires_follow_up', 'created_by', 'is_active'
    ]
    list_filter = [
        ActiveFilter, 'interaction_type', 'requires_follow_up',
        'contact', 'company', 'deal', 'created_by', 'interaction_date'
    ]
    search_fields = [
        'subject', 'description', 'contact__first_name',
        'contact__last_name', 'company__name', 'deal__title'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    fieldsets = (
        ('Interaction Details', {
            'fields': (
                'id', 'interaction_type', 'subject', 'description'
            )
        }),
        ('Timing', {
            'fields': (
                'interaction_date', 'duration_minutes'
            )
        }),
        ('Related Entities', {
            'fields': (
                'contact', 'company', 'deal'
            )
        }),
        ('Follow-up', {
            'fields': (
                'requires_follow_up', 'follow_up_date', 'follow_up_notes'
            )
        }),
        ('Created By', {
            'fields': (
                'created_by',
            )
        }),
        ('Status', {
            'fields': (
                'is_active', 'deleted_at'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'interaction_date'
    list_per_page = 25
    
    def interaction_type_display(self, obj):
        return obj.get_interaction_type_display()
    interaction_type_display.short_description = 'Type'
    interaction_type_display.admin_order_field = 'interaction_type'
    
    def contact_link(self, obj):
        if obj.contact:
            url = reverse('admin:tasks_contact_change', args=[obj.contact.id])
            return format_html('<a href="{}">{}</a>', url, obj.contact.full_name)
        return '-'
    contact_link.short_description = 'Contact'
    
    def company_link(self, obj):
        if obj.company:
            url = reverse('admin:tasks_company_change', args=[obj.company.id])
            return format_html('<a href="{}">{}</a>', url, obj.company.name)
        return '-'
    company_link.short_description = 'Company'
    
    def deal_link(self, obj):
        if obj.deal:
            url = reverse('admin:tasks_deal_change', args=[obj.deal.id])
            return format_html('<a href="{}">{}</a>', url, obj.deal.title)
        return '-'
    deal_link.short_description = 'Deal'


@admin.register(DealStageHistory)
class DealStageHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'deal_link', 'from_stage_display', 'to_stage_display',
        'changed_by', 'changed_at', 'notes_preview'
    ]
    list_filter = ['from_stage', 'to_stage', 'changed_by', 'changed_at']
    search_fields = ['deal__title', 'deal__deal_code', 'notes', 'changed_by__username']
    readonly_fields = ['id', 'changed_at']
    fieldsets = (
        ('Stage Change Details', {
            'fields': (
                'id', 'deal', 'from_stage', 'to_stage', 'notes'
            )
        }),
        ('Change Information', {
            'fields': (
                'changed_by', 'changed_at'
            )
        }),
    )
    date_hierarchy = 'changed_at'
    list_per_page = 25
    
    def deal_link(self, obj):
        url = reverse('admin:tasks_deal_change', args=[obj.deal.id])
        return format_html('<a href="{}">{}</a>', url, obj.deal.title)
    deal_link.short_description = 'Deal'
    deal_link.admin_order_field = 'deal__title'
    
    def from_stage_display(self, obj):
        return obj.get_from_stage_display()
    from_stage_display.short_description = 'From Stage'
    from_stage_display.admin_order_field = 'from_stage'
    
    def to_stage_display(self, obj):
        return obj.get_to_stage_display()
    to_stage_display.short_description = 'To Stage'
    to_stage_display.admin_order_field = 'to_stage'
    
    def notes_preview(self, obj):
        if obj.notes:
            preview = obj.notes[:50]
            if len(obj.notes) > 50:
                preview += '...'
            return preview
        return '-'
    notes_preview.short_description = 'Notes'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'digest_frequency', 'email_deal_updates', 'updated_at']
    list_filter = ['digest_frequency', 'email_deal_updates', 'email_task_reminders']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['updated_at']
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Notifications', {
            'fields': (
                'email_deal_updates', 'email_task_reminders',
                'email_weekly_digest', 'digest_frequency'
            )
        }),
        ('In-App Notifications', {
            'fields': (
                'in_app_new_assignment', 'in_app_deadline_reminder',
                'in_app_team_updates'
            )
        }),
        ('Quiet Hours', {
            'fields': (
                'quiet_hours_start', 'quiet_hours_end'
            ),
            'classes': ('collapse',)
        }),
        ('Last Updated', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 25


# Custom User Admin to link to notification preferences
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('notification_preferences_link',)
    
    def notification_preferences_link(self, obj):
        try:
            url = reverse('admin:tasks_notificationpreference_change', args=[obj.notification_preferences.id])
            return format_html('<a href="{}">⚙ Preferences</a>', url)
        except:
            url = reverse('admin:tasks_notificationpreference_add') + f'?user={obj.id}'
            return format_html('<a href="{}">Create Preferences</a>', url)
    notification_preferences_link.short_description = 'Notification Settings'


# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Admin site customization
admin.site.site_header = 'Unity Mini CRM Admin'
admin.site.site_title = 'Unity CRM Admin'
admin.site.index_title = 'CRM Administration'


# Optional: Add dashboard with custom statistics
class CRMDashboard(admin.AdminSite):
    site_header = 'Unity CRM Dashboard'
    site_title = 'CRM Dashboard'
    index_title = 'Dashboard'
    
    def index(self, request, extra_context=None):
        # Add custom statistics to the admin index
        from django.db.models import Count, Sum, Q
        from django.utils import timezone
        
        stats = {
            'total_companies': Company.objects.filter(is_active=True).count(),
            'total_contacts': Contact.objects.filter(is_active=True).count(),
            'total_deals': Deal.objects.filter(is_active=True).count(),
            'total_tasks': Task.objects.filter(is_active=True).count(),
            'overdue_tasks': Task.objects.filter(
                is_active=True,
                due_date__lt=timezone.now(),
                status__in=['pending', 'in_progress']
            ).count(),
            'recent_companies': Company.objects.filter(
                is_active=True
            ).order_by('-created_at')[:5],
        }
        
        if extra_context is None:
            extra_context = {}
        extra_context.update(stats)
        
        return super().index(request, extra_context)


# If you want to use the custom dashboard, register it separately
# crm_admin_site = CRMDashboard(name='crm_admin')
# Then use crm_admin_site.register() instead of admin.site.register()
