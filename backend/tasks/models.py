from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, URLValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid
import re


class TimestampMixin(models.Model):
    """Abstract base model with common timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """Abstract base model for soft deletion support"""
    is_active = models.BooleanField(default=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        """Soft delete the instance"""
        from django.utils import timezone
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at'])
    
    def restore(self):
        """Restore a soft-deleted instance"""
        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=['is_active', 'deleted_at'])


class Company(TimestampMixin, SoftDeleteMixin):
    """Company model representing business organizations"""
    INDUSTRY_CHOICES = [
        ('technology', 'Technology'),
        ('finance', 'Finance'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('retail', 'Retail'),
        ('manufacturing', 'Manufacturing'),
        ('consulting', 'Consulting'),
        ('other', 'Other'),
    ]
    
    SIZE_CHOICES = [
        ('micro', 'Micro (1-9)'),
        ('small', 'Small (10-49)'),
        ('medium', 'Medium (50-249)'),
        ('large', 'Large (250+)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, db_index=True)
    industry = models.CharField(
        max_length=50, 
        choices=INDUSTRY_CHOICES, 
        default='other',
        db_index=True
    )
    company_size = models.CharField(
        max_length=20, 
        choices=SIZE_CHOICES, 
        null=True, 
        blank=True
    )
    website = models.URLField(
        max_length=500, 
        blank=True, 
        validators=[URLValidator(schemes=['http', 'https'])]
    )
    phone = models.CharField(
        max_length=20, 
        blank=True,
        help_text=_("Format: +1234567890")
    )
    email = models.EmailField(blank=True, db_index=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    tags = models.CharField(
        max_length=500, 
        blank=True,
        help_text=_("Comma-separated tags for categorization")
    )
    annual_revenue = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text=_("Annual revenue in USD")
    )
    founded_year = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1800), MaxValueValidator(2100)]
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='companies'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_companies',
        help_text=_("Primary account manager")
    )

    class Meta:
        ordering = ['-created_at', 'name']
        verbose_name_plural = 'Companies'
        indexes = [
            models.Index(fields=['name', 'industry']),
            models.Index(fields=['created_at']),
            models.Index(fields=['email']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'email'],
                name='unique_company_name_email',
                condition=models.Q(email__isnull=False) & models.Q(email__gt='')
            )
        ]

    def __str__(self):
        return self.name
    
    def clean(self):
        """Custom validation"""
        super().clean()
        
        # Validate phone number format
        if self.phone and self.phone.strip():
            phone_pattern = r'^\+?1?\d{9,15}$'
            if not re.match(phone_pattern, self.phone.replace(' ', '').replace('-', '')):
                raise ValidationError({
                    'phone': _('Enter a valid phone number (e.g., +1234567890)')
                })
        
        # Validate website if provided
        if self.website and not self.website.startswith(('http://', 'https://')):
            self.website = f'https://{self.website}'
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def contact_count(self):
        """Return number of active contacts for this company"""
        return self.contacts.filter(is_active=True).count()
    
    @property
    def active_deals(self):
        """Return active deals (not won/lost)"""
        from django.db.models import Q
        return self.deals.filter(
            is_active=True,
        ).exclude(
            Q(stage='won') | Q(stage='lost')
        )
    
    @property
    def total_deal_value(self):
        """Return total value of all active deals"""
        return sum(
            deal.amount for deal in self.deals.filter(is_active=True)
            if deal.amount
        )


class Contact(TimestampMixin, SoftDeleteMixin):
    """Contact model representing individual persons"""
    SALUTATION_CHOICES = [
        ('mr', 'Mr.'),
        ('mrs', 'Mrs.'),
        ('ms', 'Ms.'),
        ('dr', 'Dr.'),
        ('prof', 'Prof.'),
    ]
    
    SOURCE_CHOICES = [
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('conference', 'Conference'),
        ('social', 'Social Media'),
        ('cold_call', 'Cold Call'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    salutation = models.CharField(
        max_length=10, 
        choices=SALUTATION_CHOICES, 
        blank=True
    )
    first_name = models.CharField(max_length=100, db_index=True)
    last_name = models.CharField(max_length=100, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(
        max_length=20, 
        blank=True,
        help_text=_("Format: +1234567890")
    )
    mobile = models.CharField(
        max_length=20, 
        blank=True,
        help_text=_("Mobile phone number")
    )
    position = models.CharField(max_length=100, blank=True, db_index=True)
    department = models.CharField(max_length=100, blank=True)
    company = models.ForeignKey(
        Company, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='contacts'
    )
    source = models.CharField(
        max_length=50, 
        choices=SOURCE_CHOICES, 
        default='other',
        db_index=True
    )
    is_decision_maker = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    tags = models.CharField(
        max_length=500, 
        blank=True,
        help_text=_("Comma-separated tags for categorization")
    )
    social_linkedin = models.URLField(max_length=500, blank=True)
    social_twitter = models.URLField(max_length=500, blank=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='contacts'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_contacts',
        help_text=_("Primary relationship manager")
    )

    class Meta:
        ordering = ['-created_at', 'last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['email']),
            models.Index(fields=['company', 'position']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'company'],
                name='unique_contact_email_company',
                condition=models.Q(company__isnull=False)
            )
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        """Custom validation"""
        super().clean()
        
        # Validate phone numbers
        phone_fields = ['phone', 'mobile']
        for field_name in phone_fields:
            field_value = getattr(self, field_name, '')
            if field_value and field_value.strip():
                phone_pattern = r'^\+?1?\d{9,15}$'
                if not re.match(phone_pattern, field_value.replace(' ', '').replace('-', '')):
                    raise ValidationError({
                        field_name: _('Enter a valid phone number (e.g., +1234567890)')
                    })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        """Return full name with salutation if available"""
        if self.salutation:
            return f"{self.get_salutation_display()} {self.first_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        from datetime import date
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    @property
    def recent_interactions(self):
        """Get recent interactions with this contact"""
        from .interaction import Interaction
        return Interaction.objects.filter(
            contact=self,
            is_active=True
        ).order_by('-interaction_date')[:5]


class Deal(TimestampMixin, SoftDeleteMixin):
    """Deal model representing sales opportunities"""
    STAGE_CHOICES = [
        ('lead', 'Lead'),
        ('qualified', 'Qualified'),
        ('proposal', 'Proposal'),
        ('negotiation', 'Negotiation'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
        ('on_hold', 'On Hold'),
    ]
    
    LOST_REASON_CHOICES = [
        ('price', 'Price'),
        ('competitor', 'Competitor'),
        ('timing', 'Timing'),
        ('features', 'Missing Features'),
        ('other', 'Other'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CAD', 'Canadian Dollar'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deal_code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text=_("Unique deal identifier (e.g., DEAL-2024-001)")
    )
    title = models.CharField(max_length=200, db_index=True)
    amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(
        max_length=3, 
        choices=CURRENCY_CHOICES, 
        default='USD'
    )
    stage = models.CharField(
        max_length=20, 
        choices=STAGE_CHOICES, 
        default='lead',
        db_index=True
    )
    probability = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Win probability (0-100%)')
    )
    expected_close_date = models.DateField(null=True, blank=True, db_index=True)
    actual_close_date = models.DateField(null=True, blank=True)
    lost_reason = models.CharField(
        max_length=50, 
        choices=LOST_REASON_CHOICES, 
        blank=True
    )
    lost_notes = models.TextField(blank=True)
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='deals'
    )
    contact = models.ForeignKey(
        Contact, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='deals'
    )
    notes = models.TextField(blank=True)
    tags = models.CharField(max_length=500, blank=True)
    
    # Team assignment
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_deals'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_deals',
        help_text=_("Primary sales representative")
    )
    team_members = models.ManyToManyField(
        User,
        related_name='team_deals',
        blank=True,
        help_text=_("Additional team members working on this deal")
    )
    
    # Performance tracking
    last_contact_date = models.DateField(null=True, blank=True)
    next_follow_up = models.DateField(null=True, blank=True)
    forecast_category = models.CharField(
        max_length=50,
        choices=[
            ('pipeline', 'Pipeline'),
            ('best_case', 'Best Case'),
            ('commit', 'Commit'),
            ('closed', 'Closed'),
        ],
        default='pipeline'
    )

    class Meta:
        ordering = ['-created_at', '-expected_close_date']
        indexes = [
            models.Index(fields=['deal_code']),
            models.Index(fields=['stage', 'expected_close_date']),
            models.Index(fields=['company', 'stage']),
            models.Index(fields=['assigned_to', 'stage']),
            models.Index(fields=['probability']),
        ]

    def __str__(self):
        return f"{self.deal_code}: {self.title}"

    def clean(self):
        """Custom validation"""
        super().clean()
        
        # Validate probability based on stage
        stage_probability_map = {
            'lead': (0, 30),
            'qualified': (30, 50),
            'proposal': (50, 70),
            'negotiation': (70, 90),
            'closed_won': (95, 100),
            'closed_lost': (0, 5),
            'on_hold': (0, 100),
        }
        
        if self.stage in stage_probability_map:
            min_prob, max_prob = stage_probability_map[self.stage]
            if not (min_prob <= self.probability <= max_prob):
                raise ValidationError({
                    'probability': _(
                        f'Probability should be between {min_prob}-{max_prob}% for {self.get_stage_display()} stage'
                    )
                })
        
        # Validate close dates
        if self.actual_close_date and self.expected_close_date:
            if self.actual_close_date < self.expected_close_date:
                raise ValidationError({
                    'actual_close_date': _('Actual close date cannot be before expected close date')
                })
    
    def save(self, *args, **kwargs):
        # Auto-generate deal code if not provided
        if not self.deal_code:
            from django.db.models import Max
            last_deal = Deal.objects.filter(
                deal_code__regex=r'^DEAL-\d{4}-\d{3}$'
            ).aggregate(Max('deal_code'))
            
            if last_deal['deal_code__max']:
                last_num = int(last_deal['deal_code__max'].split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            from datetime import datetime
            year = datetime.now().year
            self.deal_code = f"DEAL-{year}-{new_num:03d}"
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def weighted_amount(self):
        """Calculate weighted deal amount (amount * probability)"""
        return (self.amount * self.probability) / 100
    
    @property
    def days_in_stage(self):
        """Calculate days in current stage"""
        from django.utils import timezone
        from .deal_stage_history import DealStageHistory
        
        latest_history = DealStageHistory.objects.filter(
            deal=self
        ).order_by('-changed_at').first()
        
        if latest_history:
            days = (timezone.now().date() - latest_history.changed_at.date()).days
            return max(0, days)
        return 0
    
    @property
    def is_closed(self):
        """Check if deal is closed (won or lost)"""
        return self.stage in ['closed_won', 'closed_lost']
    
    def close_deal(self, stage, lost_reason='', lost_notes=''):
        """Helper method to close a deal"""
        from django.utils import timezone
        
        if stage not in ['closed_won', 'closed_lost']:
            raise ValidationError(_("Stage must be 'closed_won' or 'closed_lost'"))
        
        self.stage = stage
        self.actual_close_date = timezone.now().date()
        self.probability = 100 if stage == 'closed_won' else 0
        
        if stage == 'closed_lost':
            self.lost_reason = lost_reason
            self.lost_notes = lost_notes
        
        self.save()


class Task(TimestampMixin, SoftDeleteMixin):
    """Task model for tracking activities and to-dos"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('deferred', 'Deferred'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    TASK_TYPE_CHOICES = [
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('follow_up', 'Follow Up'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    task_type = models.CharField(
        max_length=20, 
        choices=TASK_TYPE_CHOICES, 
        default='other',
        db_index=True
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        db_index=True
    )
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='medium',
        db_index=True
    )
    due_date = models.DateTimeField(null=True, blank=True, db_index=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text=_("Estimated hours to complete")
    )
    actual_hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text=_("Actual hours spent")
    )
    
    # Relationships
    contact = models.ForeignKey(
        Contact, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='tasks'
    )
    deal = models.ForeignKey(
        Deal, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='tasks'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tasks'
    )
    
    # Team assignment
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_tasks'
    )
    
    # Task metadata
    recurrence_pattern = models.CharField(
        max_length=100, 
        blank=True,
        help_text=_("Cron-like pattern for recurring tasks")
    )
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks'
    )
    tags = models.CharField(max_length=500, blank=True)
    attachment = models.FileField(
        upload_to='task_attachments/',
        null=True,
        blank=True,
        help_text=_("Related file attachment")
    )

    class Meta:
        ordering = ['priority', 'due_date', '-created_at']
        indexes = [
            models.Index(fields=['due_date', 'priority']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['contact', 'deal', 'company']),
            models.Index(fields=['status', 'completed_date']),
        ]
        permissions = [
            ('can_reassign_task', 'Can reassign tasks to other users'),
            ('can_close_task', 'Can close completed tasks'),
            ('can_view_all_tasks', 'Can view all tasks regardless of assignment'),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"

    def clean(self):
        """Custom validation"""
        super().clean()
        
        # Validate due date
        from django.utils import timezone
        if self.due_date and self.due_date < timezone.now():
            if self.status != 'completed':
                raise ValidationError({
                    'due_date': _('Due date cannot be in the past for pending tasks')
                })
        
        # Validate estimated vs actual hours
        if self.estimated_hours and self.estimated_hours <= 0:
            raise ValidationError({
                'estimated_hours': _('Estimated hours must be greater than 0')
            })
        
        if self.actual_hours and self.actual_hours < 0:
            raise ValidationError({
                'actual_hours': _('Actual hours cannot be negative')
            })
    
    def save(self, *args, **kwargs):
        # Set completed_date if status changes to completed
        from django.utils import timezone
        if self.status == 'completed' and not self.completed_date:
            self.completed_date = timezone.now()
        elif self.status != 'completed' and self.completed_date:
            self.completed_date = None
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        from django.utils import timezone
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return self.due_date < timezone.now()
        return False
    
    @property
    def days_overdue(self):
        """Calculate days overdue"""
        from django.utils import timezone
        if self.is_overdue:
            days = (timezone.now() - self.due_date).days
            return max(0, days)
        return 0
    
    @property
    def completion_rate(self):
        """Calculate completion rate based on actual vs estimated hours"""
        if self.estimated_hours and self.actual_hours:
            if self.estimated_hours > 0:
                return (self.actual_hours / self.estimated_hours) * 100
        return 0
    
    @property
    def related_entity(self):
        """Get the main related entity (contact, deal, or company)"""
        if self.contact:
            return self.contact
        elif self.deal:
            return self.deal
        elif self.company:
            return self.company
        return None
    
    def complete_task(self, actual_hours=None, notes=''):
        """Helper method to complete a task"""
        from django.utils import timezone
        
        self.status = 'completed'
        self.completed_date = timezone.now()
        
        if actual_hours is not None:
            self.actual_hours = actual_hours
        
        if notes and not self.description.endswith(f"\n\nCompletion Notes: {notes}"):
            self.description += f"\n\nCompletion Notes: {notes}"
        
        self.save()
    
    def get_subtasks(self):
        """Get all subtasks recursively"""
        subtasks = list(self.subtasks.all())
        for subtask in subtasks:
            subtasks.extend(subtask.get_subtasks())
        return subtasks


# New supporting models for enhanced functionality

class Interaction(TimestampMixin, SoftDeleteMixin):
    """Track interactions with contacts/companies"""
    INTERACTION_TYPES = [
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('note', 'Note'),
        ('demo', 'Product Demo'),
        ('proposal', 'Proposal Sent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    interaction_date = models.DateTimeField(db_index=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Relationships
    contact = models.ForeignKey(
        Contact, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='interactions'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='interactions'
    )
    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='interactions'
    )
    
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='interactions'
    )
    
    # Follow-up
    requires_follow_up = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-interaction_date']
        indexes = [
            models.Index(fields=['interaction_date', 'interaction_type']),
            models.Index(fields=['contact', 'company', 'deal']),
        ]


class DealStageHistory(TimestampMixin):
    """Track history of deal stage changes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='stage_history')
    from_stage = models.CharField(max_length=20, choices=Deal.STAGE_CHOICES)
    to_stage = models.CharField(max_length=20, choices=Deal.STAGE_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Deal Stage Histories'


class NotificationPreference(models.Model):
    """User notification preferences linked to UserProfile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notifications
    email_deal_updates = models.BooleanField(default=True)
    email_task_reminders = models.BooleanField(default=True)
    email_weekly_digest = models.BooleanField(default=True)
    
    # In-app notifications
    in_app_new_assignment = models.BooleanField(default=True)
    in_app_deadline_reminder = models.BooleanField(default=True)
    in_app_team_updates = models.BooleanField(default=True)
    
    # Frequency
    digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )
    
    # Quiet hours
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"
