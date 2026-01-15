from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Company, Contact, Deal, Task, 
    Interaction, DealStageHistory, NotificationPreference
)
import uuid


# Helper serializers
class UserSimpleSerializer(serializers.ModelSerializer):
    """Simple user serializer for nested relationships"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}" if obj.first_name or obj.last_name else obj.username


class CompanyNestedSerializer(serializers.ModelSerializer):
    """Nested company serializer for use in other serializers"""
    industry_display = serializers.CharField(source='get_industry_display', read_only=True)
    company_size_display = serializers.CharField(source='get_company_size_display', read_only=True)
    
    class Meta:
        model = Company
        fields = ['id', 'name', 'industry', 'industry_display', 'company_size', 
                 'company_size_display', 'phone', 'email', 'website']
        read_only_fields = fields


class ContactNestedSerializer(serializers.ModelSerializer):
    """Nested contact serializer for use in other serializers"""
    full_name = serializers.SerializerMethodField()
    salutation_display = serializers.CharField(source='get_salutation_display', read_only=True)
    
    class Meta:
        model = Contact
        fields = ['id', 'full_name', 'first_name', 'last_name', 'salutation', 
                 'salutation_display', 'email', 'phone', 'position', 'company']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return obj.full_name


class DealNestedSerializer(serializers.ModelSerializer):
    """Nested deal serializer for use in other serializers"""
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    
    class Meta:
        model = Deal
        fields = ['id', 'deal_code', 'title', 'amount', 'currency', 'currency_display',
                 'stage', 'stage_display', 'probability', 'company', 'contact']
        read_only_fields = fields


# Main serializers
class CompanySerializer(serializers.ModelSerializer):
    """Main company serializer with full details"""
    id = serializers.UUIDField(read_only=True, default=uuid.uuid4)
    industry_display = serializers.CharField(source='get_industry_display', read_only=True)
    company_size_display = serializers.CharField(source='get_company_size_display', read_only=True)
    created_by = UserSimpleSerializer(read_only=True)
    assigned_to = UserSimpleSerializer(read_only=True)
    contact_count = serializers.IntegerField(read_only=True)
    active_deals = DealNestedSerializer(many=True, read_only=True, source='deals.filter(is_active=True)')
    total_deal_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    # For write operations
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='created_by',
        required=False
    )
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='assigned_to',
        required=False
    )
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'industry', 'industry_display', 'company_size', 
            'company_size_display', 'website', 'phone', 'email', 'address',
            'city', 'state', 'country', 'postal_code', 'notes', 'tags',
            'annual_revenue', 'founded_year', 'is_active', 'deleted_at',
            'created_at', 'updated_at', 'created_by', 'created_by_id',
            'assigned_to', 'assigned_to_id', 'contact_count',
            'active_deals', 'total_deal_value'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at',
                           'contact_count', 'total_deal_value', 'industry_display',
                           'company_size_display']
    
    def validate(self, data):
        """Custom validation for company data"""
        # Validate website format
        website = data.get('website', '')
        if website and not website.startswith(('http://', 'https://')):
            data['website'] = f'https://{website}'
        
        # Validate phone format
        phone = data.get('phone', '')
        if phone:
            import re
            phone_pattern = r'^\+?1?\d{9,15}$'
            if not re.match(phone_pattern, phone.replace(' ', '').replace('-', '')):
                raise serializers.ValidationError({
                    'phone': 'Enter a valid phone number (e.g., +1234567890)'
                })
        
        # Validate email uniqueness with name
        if data.get('email') and data.get('name'):
            existing = Company.objects.filter(
                email=data['email'],
                name=data['name']
            ).exclude(pk=self.instance.pk if self.instance else None)
            if existing.exists():
                raise serializers.ValidationError({
                    'email': 'A company with this email and name already exists.'
                })
        
        return data
    
    def create(self, validated_data):
        """Handle company creation with default values"""
        # Set created_by to current user if not specified
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if 'created_by' not in validated_data:
                validated_data['created_by'] = request.user
        
        return super().create(validated_data)


class ContactSerializer(serializers.ModelSerializer):
    """Main contact serializer with full details"""
    id = serializers.UUIDField(read_only=True, default=uuid.uuid4)
    full_name = serializers.SerializerMethodField(read_only=True)
    salutation_display = serializers.CharField(source='get_salutation_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    age = serializers.IntegerField(read_only=True)
    company_details = CompanyNestedSerializer(source='company', read_only=True)
    created_by = UserSimpleSerializer(read_only=True)
    assigned_to = UserSimpleSerializer(read_only=True)
    
    # For write operations
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        write_only=True,
        source='company',
        required=False,
        allow_null=True
    )
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='created_by',
        required=False
    )
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='assigned_to',
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Contact
        fields = [
            'id', 'salutation', 'salutation_display', 'first_name', 'last_name',
            'full_name', 'email', 'phone', 'mobile', 'position', 'department',
            'company', 'company_id', 'company_details', 'source', 'source_display',
            'is_decision_maker', 'date_of_birth', 'age', 'notes', 'tags',
            'social_linkedin', 'social_twitter', 'is_active', 'deleted_at',
            'created_at', 'updated_at', 'created_by', 'created_by_id',
            'assigned_to', 'assigned_to_id'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at',
                           'full_name', 'age', 'salutation_display', 'source_display']
        extra_kwargs = {
            'email': {'validators': []}  # We'll handle uniqueness in validate
        }
    
    def get_full_name(self, obj):
        return obj.full_name
    
    def validate(self, data):
        """Custom validation for contact data"""
        # Validate phone numbers
        import re
        phone_fields = ['phone', 'mobile']
        for field_name in phone_fields:
            if field_name in data and data[field_name]:
                phone_pattern = r'^\+?1?\d{9,15}$'
                phone_value = data[field_name].replace(' ', '').replace('-', '')
                if not re.match(phone_pattern, phone_value):
                    raise serializers.ValidationError({
                        field_name: 'Enter a valid phone number (e.g., +1234567890)'
                    })
        
        # Validate email uniqueness with company
        email = data.get('email')
        company = data.get('company')
        
        if email and company:
            existing = Contact.objects.filter(
                email=email,
                company=company
            ).exclude(pk=self.instance.pk if self.instance else None)
            if existing.exists():
                raise serializers.ValidationError({
                    'email': 'A contact with this email already exists at this company.'
                })
        
        return data
    
    def create(self, validated_data):
        """Handle contact creation with default values"""
        # Set created_by to current user if not specified
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if 'created_by' not in validated_data:
                validated_data['created_by'] = request.user
        
        return super().create(validated_data)


class DealSerializer(serializers.ModelSerializer):
    """Main deal serializer with full details"""
    id = serializers.UUIDField(read_only=True, default=uuid.uuid4)
    deal_code = serializers.CharField(read_only=True)  # Auto-generated
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    lost_reason_display = serializers.CharField(source='get_lost_reason_display', read_only=True)
    forecast_category_display = serializers.CharField(source='get_forecast_category_display', read_only=True)
    weighted_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    days_in_stage = serializers.IntegerField(read_only=True)
    is_closed = serializers.BooleanField(read_only=True)
    
    # Nested relationships
    company_details = CompanyNestedSerializer(source='company', read_only=True)
    contact_details = ContactNestedSerializer(source='contact', read_only=True)
    created_by = UserSimpleSerializer(read_only=True)
    assigned_to = UserSimpleSerializer(read_only=True)
    team_members = UserSimpleSerializer(many=True, read_only=True)
    
    # For write operations
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.filter(is_active=True),
        write_only=True,
        source='company'
    )
    contact_id = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.filter(is_active=True),
        write_only=True,
        source='contact',
        required=False,
        allow_null=True
    )
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='created_by',
        required=False
    )
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='assigned_to',
        required=False,
        allow_null=True
    )
    team_member_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='team_members',
        many=True,
        required=False
    )
    
    class Meta:
        model = Deal
        fields = [
            'id', 'deal_code', 'title', 'amount', 'currency', 'currency_display',
            'stage', 'stage_display', 'probability', 'weighted_amount',
            'expected_close_date', 'actual_close_date', 'lost_reason',
            'lost_reason_display', 'lost_notes', 'company', 'company_id',
            'company_details', 'contact', 'contact_id', 'contact_details',
            'notes', 'tags', 'is_active', 'deleted_at', 'created_at',
            'updated_at', 'created_by', 'created_by_id', 'assigned_to',
            'assigned_to_id', 'team_members', 'team_member_ids',
            'last_contact_date', 'next_follow_up', 'forecast_category',
            'forecast_category_display', 'days_in_stage', 'is_closed'
        ]
        read_only_fields = [
            'id', 'deal_code', 'created_at', 'updated_at', 'deleted_at',
            'stage_display', 'currency_display', 'lost_reason_display',
            'forecast_category_display', 'weighted_amount', 'days_in_stage',
            'is_closed'
        ]
    
    def validate(self, data):
        """Custom validation for deal data"""
        from django.utils import timezone
        
        # Validate probability based on stage
        stage = data.get('stage', self.instance.stage if self.instance else 'lead')
        probability = data.get('probability', self.instance.probability if self.instance else 0)
        
        stage_probability_map = {
            'lead': (0, 30),
            'qualified': (30, 50),
            'proposal': (50, 70),
            'negotiation': (70, 90),
            'closed_won': (95, 100),
            'closed_lost': (0, 5),
            'on_hold': (0, 100),
        }
        
        if stage in stage_probability_map:
            min_prob, max_prob = stage_probability_map[stage]
            if not (min_prob <= probability <= max_prob):
                raise serializers.ValidationError({
                    'probability': f'Probability should be between {min_prob}-{max_prob}% for {stage} stage'
                })
        
        # Validate close dates
        expected_close = data.get('expected_close_date')
        actual_close = data.get('actual_close_date')
        
        if actual_close and expected_close:
            if actual_close < expected_close:
                raise serializers.ValidationError({
                    'actual_close_date': 'Actual close date cannot be before expected close date'
                })
        
        # Auto-update last_contact_date if stage changes
        if 'stage' in data and data['stage'] != getattr(self.instance, 'stage', None):
            data['last_contact_date'] = timezone.now().date()
        
        return data
    
    def create(self, validated_data):
        """Handle deal creation with auto-generated deal code"""
        # Extract team members for ManyToMany handling
        team_members = validated_data.pop('team_members', [])
        
        # Set created_by to current user if not specified
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if 'created_by' not in validated_data:
                validated_data['created_by'] = request.user
        
        # Create deal instance
        deal = super().create(validated_data)
        
        # Add team members
        if team_members:
            deal.team_members.set(team_members)
        
        return deal
    
    def update(self, instance, validated_data):
        """Handle deal update with team members"""
        # Extract team members for ManyToMany handling
        team_members = validated_data.pop('team_members', None)
        
        # Update deal instance
        deal = super().update(instance, validated_data)
        
        # Update team members if provided
        if team_members is not None:
            deal.team_members.set(team_members)
        
        return deal


class TaskSerializer(serializers.ModelSerializer):
    """Main task serializer with full details"""
    id = serializers.UUIDField(read_only=True, default=uuid.uuid4)
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    completion_rate = serializers.FloatField(read_only=True)
    
    # Nested relationships
    contact_details = ContactNestedSerializer(source='contact', read_only=True)
    deal_details = DealNestedSerializer(source='deal', read_only=True)
    company_details = CompanyNestedSerializer(source='company', read_only=True)
    assigned_to = UserSimpleSerializer(read_only=True)
    created_by = UserSimpleSerializer(read_only=True)
    parent_task_details = serializers.SerializerMethodField()
    
    # For write operations
    contact_id = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.filter(is_active=True),
        write_only=True,
        source='contact',
        required=False,
        allow_null=True
    )
    deal_id = serializers.PrimaryKeyRelatedField(
        queryset=Deal.objects.filter(is_active=True),
        write_only=True,
        source='deal',
        required=False,
        allow_null=True
    )
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.filter(is_active=True),
        write_only=True,
        source='company',
        required=False,
        allow_null=True
    )
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='assigned_to',
        required=False,
        allow_null=True
    )
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='created_by',
        required=False
    )
    parent_task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.filter(is_active=True),
        write_only=True,
        source='parent_task',
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'task_type', 'task_type_display',
            'status', 'status_display', 'priority', 'priority_display',
            'due_date', 'completed_date', 'estimated_hours', 'actual_hours',
            'contact', 'contact_id', 'contact_details', 'deal', 'deal_id',
            'deal_details', 'company', 'company_id', 'company_details',
            'assigned_to', 'assigned_to_id', 'created_by', 'created_by_id',
            'recurrence_pattern', 'parent_task', 'parent_task_id', 'parent_task_details',
            'tags', 'attachment', 'is_active', 'deleted_at', 'created_at',
            'updated_at', 'is_overdue', 'days_overdue', 'completion_rate'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'deleted_at',
            'task_type_display', 'status_display', 'priority_display',
            'is_overdue', 'days_overdue', 'completion_rate'
        ]
    
    def get_parent_task_details(self, obj):
        if obj.parent_task:
            return {
                'id': obj.parent_task.id,
                'title': obj.parent_task.title,
                'status': obj.parent_task.status,
                'status_display': obj.parent_task.get_status_display()
            }
        return None
    
    def validate(self, data):
        """Custom validation for task data"""
        from django.utils import timezone
        
        # Validate due date
        due_date = data.get('due_date')
        status = data.get('status', getattr(self.instance, 'status', 'pending'))
        
        if due_date and due_date < timezone.now() and status != 'completed':
            raise serializers.ValidationError({
                'due_date': 'Due date cannot be in the past for pending tasks'
            })
        
        # Validate hours
        estimated_hours = data.get('estimated_hours')
        actual_hours = data.get('actual_hours')
        
        if estimated_hours is not None and estimated_hours <= 0:
            raise serializers.ValidationError({
                'estimated_hours': 'Estimated hours must be greater than 0'
            })
        
        if actual_hours is not None and actual_hours < 0:
            raise serializers.ValidationError({
                'actual_hours': 'Actual hours cannot be negative'
            })
        
        return data
    
    def create(self, validated_data):
        """Handle task creation"""
        # Set created_by to current user if not specified
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if 'created_by' not in validated_data:
                validated_data['created_by'] = request.user
        
        return super().create(validated_data)


# Supporting model serializers
class InteractionSerializer(serializers.ModelSerializer):
    """Serializer for interaction tracking"""
    id = serializers.UUIDField(read_only=True, default=uuid.uuid4)
    interaction_type_display = serializers.CharField(source='get_interaction_type_display', read_only=True)
    
    contact_details = ContactNestedSerializer(source='contact', read_only=True)
    company_details = CompanyNestedSerializer(source='company', read_only=True)
    deal_details = DealNestedSerializer(source='deal', read_only=True)
    created_by = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = Interaction
        fields = [
            'id', 'interaction_type', 'interaction_type_display', 'subject',
            'description', 'interaction_date', 'duration_minutes',
            'contact', 'contact_details', 'company', 'company_details',
            'deal', 'deal_details', 'created_by', 'requires_follow_up',
            'follow_up_date', 'follow_up_notes', 'is_active', 'deleted_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class DealStageHistorySerializer(serializers.ModelSerializer):
    """Serializer for deal stage change history"""
    id = serializers.UUIDField(read_only=True, default=uuid.uuid4)
    from_stage_display = serializers.CharField(source='get_from_stage_display', read_only=True)
    to_stage_display = serializers.CharField(source='get_to_stage_display', read_only=True)
    changed_by = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = DealStageHistory
        fields = [
            'id', 'deal', 'from_stage', 'from_stage_display',
            'to_stage', 'to_stage_display', 'changed_by',
            'changed_at', 'notes'
        ]
        read_only_fields = fields


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user notification preferences"""
    user = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = NotificationPreference
        fields = [
            'user', 'email_deal_updates', 'email_task_reminders',
            'email_weekly_digest', 'in_app_new_assignment',
            'in_app_deadline_reminder', 'in_app_team_updates',
            'digest_frequency', 'quiet_hours_start', 'quiet_hours_end',
            'updated_at'
        ]
        read_only_fields = ['user', 'updated_at']


# Dashboard and statistics serializers
class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_companies = serializers.IntegerField()
    total_contacts = serializers.IntegerField()
    total_deals = serializers.IntegerField()
    total_tasks = serializers.IntegerField()
    active_deals_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    weighted_deals_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    overdue_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    
    # Deal pipeline by stage
    deal_pipeline = serializers.DictField(child=serializers.IntegerField())
    
    # Recent activities
    recent_companies = CompanyNestedSerializer(many=True)
    recent_contacts = ContactNestedSerializer(many=True)
    recent_deals = DealNestedSerializer(many=True)
    recent_tasks = TaskSerializer(many=True)


# List serializers for optimized responses
class CompanyListSerializer(serializers.ModelSerializer):
    """Optimized serializer for company lists"""
    industry_display = serializers.CharField(source='get_industry_display', read_only=True)
    contact_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'industry', 'industry_display', 'company_size',
            'phone', 'email', 'website', 'contact_count', 'is_active',
            'created_at', 'updated_at'
        ]


class ContactListSerializer(serializers.ModelSerializer):
    """Optimized serializer for contact lists"""
    full_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Contact
        fields = [
            'id', 'full_name', 'email', 'phone', 'position',
            'company', 'company_name', 'is_decision_maker', 'is_active',
            'created_at', 'updated_at'
        ]
    
    def get_full_name(self, obj):
        return obj.full_name


class DealListSerializer(serializers.ModelSerializer):
    """Optimized serializer for deal lists"""
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    
    class Meta:
        model = Deal
        fields = [
            'id', 'deal_code', 'title', 'amount', 'currency', 'stage',
            'stage_display', 'probability', 'company', 'company_name',
            'contact', 'contact_name', 'expected_close_date', 'is_active',
            'created_at', 'updated_at'
        ]


class TaskListSerializer(serializers.ModelSerializer):
    """Optimized serializer for task lists"""
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'task_type', 'priority', 'priority_display',
            'status', 'status_display', 'due_date', 'assigned_to',
            'assigned_to_name', 'is_overdue', 'is_active', 'created_at',
            'updated_at'
        ]
