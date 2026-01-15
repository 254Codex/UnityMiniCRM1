from rest_framework import generics, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg, F, When, Case, IntegerField
from django.db.models.functions import ExtractMonth, ExtractYear, TruncDate
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta
import uuid

from .models import (
    Company, Contact, Deal, Task, 
    Interaction, DealStageHistory, NotificationPreference
)
from .serializers import (
    CompanySerializer, CompanyListSerializer,
    ContactSerializer, ContactListSerializer,
    DealSerializer, DealListSerializer,
    TaskSerializer, TaskListSerializer,
    InteractionSerializer, DealStageHistorySerializer,
    NotificationPreferenceSerializer, DashboardStatsSerializer,
    UserSimpleSerializer
)
from django.contrib.auth.models import User


class BaseCRUDViewSet(viewsets.ModelViewSet):
    """Base viewset with common functionality"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    def get_queryset(self):
        """Override to filter by active status by default"""
        queryset = super().get_queryset()
        
        # Filter out soft-deleted records by default
        if hasattr(self.model, 'is_active'):
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by to current user if not specified"""
        if self.request.user.is_authenticated:
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to support soft delete"""
        instance = self.get_object()
        
        # Check if model supports soft delete
        if hasattr(instance, 'soft_delete'):
            instance.soft_delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        # Otherwise use hard delete
        return super().destroy(request, *args, **kwargs)


# Company Views
class CompanyViewSet(BaseCRUDViewSet):
    """Viewset for Company CRUD operations"""
    model = Company
    search_fields = ['name', 'industry', 'email', 'phone', 'city', 'state', 'country']
    filterset_fields = ['industry', 'company_size', 'is_active']
    ordering_fields = ['name', 'created_at', 'updated_at', 'annual_revenue']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail"""
        if self.action == 'list':
            return CompanyListSerializer
        return CompanySerializer
    
    def get_queryset(self):
        """Custom queryset with annotations"""
        queryset = super().get_queryset()
        
        # Annotate with contact count
        queryset = queryset.annotate(
            contact_count=Count('contacts', filter=Q(contacts__is_active=True))
        )
        
        # Filter by tags if provided
        tags = self.request.query_params.get('tags', None)
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            queries = Q()
            for tag in tag_list:
                queries |= Q(tags__icontains=tag)
            queryset = queryset.filter(queries)
        
        # Filter by revenue range
        min_revenue = self.request.query_params.get('min_revenue', None)
        max_revenue = self.request.query_params.get('max_revenue', None)
        
        if min_revenue:
            queryset = queryset.filter(annual_revenue__gte=min_revenue)
        if max_revenue:
            queryset = queryset.filter(annual_revenue__lte=max_revenue)
        
        # Filter by created date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        """Get all contacts for a company"""
        company = self.get_object()
        contacts = company.contacts.filter(is_active=True)
        serializer = ContactListSerializer(contacts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def deals(self, request, pk=None):
        """Get all deals for a company"""
        company = self.get_object()
        deals = company.deals.filter(is_active=True)
        serializer = DealListSerializer(deals, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get company statistics"""
        company = self.get_object()
        
        stats = {
            'total_contacts': company.contacts.filter(is_active=True).count(),
            'total_deals': company.deals.filter(is_active=True).count(),
            'active_deals': company.deals.filter(
                is_active=True
            ).exclude(
                Q(stage='closed_won') | Q(stage='closed_lost')
            ).count(),
            'total_deal_value': company.deals.filter(is_active=True).aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'weighted_deal_value': company.deals.filter(is_active=True).aggregate(
                total=Sum(F('amount') * F('probability') / 100.0)
            )['total'] or 0,
            'recent_interactions': company.interactions.filter(
                is_active=True
            ).order_by('-interaction_date')[:5].count()
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def industries(self, request):
        """Get list of all industries with counts"""
        industries = Company.objects.filter(is_active=True).values(
            'industry'
        ).annotate(
            count=Count('id'),
            total_revenue=Sum('annual_revenue')
        ).order_by('-count')
        
        return Response(industries)


# Contact Views
class ContactViewSet(BaseCRUDViewSet):
    """Viewset for Contact CRUD operations"""
    model = Contact
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'position', 'department', 'company__name']
    filterset_fields = ['source', 'is_decision_maker', 'company', 'is_active']
    ordering_fields = ['last_name', 'first_name', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail"""
        if self.action == 'list':
            return ContactListSerializer
        return ContactSerializer
    
    def get_queryset(self):
        """Custom queryset with annotations"""
        queryset = super().get_queryset()
        
        # Filter by company if provided
        company_id = self.request.query_params.get('company_id', None)
        if company_id:
            try:
                company_uuid = uuid.UUID(company_id)
                queryset = queryset.filter(company_id=company_uuid)
            except ValueError:
                pass
        
        # Filter by decision maker status
        is_decision_maker = self.request.query_params.get('is_decision_maker', None)
        if is_decision_maker is not None:
            queryset = queryset.filter(is_decision_maker=is_decision_maker.lower() == 'true')
        
        # Filter by tags
        tags = self.request.query_params.get('tags', None)
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            queries = Q()
            for tag in tag_list:
                queries |= Q(tags__icontains=tag)
            queryset = queryset.filter(queries)
        
        # Annotate with interaction count
        queryset = queryset.annotate(
            interaction_count=Count('interactions', filter=Q(interactions__is_active=True))
        )
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def interactions(self, request, pk=None):
        """Get all interactions for a contact"""
        contact = self.get_object()
        interactions = contact.interactions.filter(is_active=True).order_by('-interaction_date')
        serializer = InteractionSerializer(interactions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Get all tasks for a contact"""
        contact = self.get_object()
        tasks = contact.tasks.filter(is_active=True)
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sources(self, request):
        """Get list of all contact sources with counts"""
        sources = Contact.objects.filter(is_active=True).values(
            'source'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response(sources)


# Deal Views
class DealViewSet(BaseCRUDViewSet):
    """Viewset for Deal CRUD operations"""
    model = Deal
    search_fields = ['title', 'deal_code', 'company__name', 'contact__first_name', 'contact__last_name']
    filterset_fields = ['stage', 'currency', 'company', 'assigned_to', 'is_active']
    ordering_fields = ['expected_close_date', 'amount', 'probability', 'created_at', 'updated_at']
    ordering = ['-expected_close_date']
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail"""
        if self.action == 'list':
            return DealListSerializer
        return DealSerializer
    
    def get_queryset(self):
        """Custom queryset with annotations"""
        queryset = super().get_queryset()
        
        # Filter by stage
        stage = self.request.query_params.get('stage', None)
        if stage:
            queryset = queryset.filter(stage=stage)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(expected_close_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(expected_close_date__lte=end_date)
        
        # Filter by probability range
        min_prob = self.request.query_params.get('min_probability', None)
        max_prob = self.request.query_params.get('max_probability', None)
        
        if min_prob:
            queryset = queryset.filter(probability__gte=min_prob)
        if max_prob:
            queryset = queryset.filter(probability__lte=max_prob)
        
        # Filter by amount range
        min_amount = self.request.query_params.get('min_amount', None)
        max_amount = self.request.query_params.get('max_amount', None)
        
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)
        
        # Filter by assigned_to
        assigned_to = self.request.query_params.get('assigned_to', None)
        if assigned_to:
            try:
                user_uuid = uuid.UUID(assigned_to)
                queryset = queryset.filter(assigned_to_id=user_uuid)
            except (ValueError, User.DoesNotExist):
                pass
        
        # Annotate with weighted amount
        queryset = queryset.annotate(
            weighted_amount=F('amount') * F('probability') / 100.0
        )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def change_stage(self, request, pk=None):
        """Change deal stage with history tracking"""
        deal = self.get_object()
        new_stage = request.data.get('stage')
        notes = request.data.get('notes', '')
        
        if not new_stage:
            return Response(
                {'error': 'Stage is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate stage
        valid_stages = [choice[0] for choice in Deal.STAGE_CHOICES]
        if new_stage not in valid_stages:
            return Response(
                {'error': f'Invalid stage. Valid stages are: {", ".join(valid_stages)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create stage history
        DealStageHistory.objects.create(
            deal=deal,
            from_stage=deal.stage,
            to_stage=new_stage,
            changed_by=request.user,
            notes=notes
        )
        
        # Update deal
        deal.stage = new_stage
        
        # Update probability based on stage
        stage_probability_map = {
            'lead': 20, 'qualified': 40, 'proposal': 60,
            'negotiation': 80, 'closed_won': 100, 'closed_lost': 0,
            'on_hold': 50
        }
        if new_stage in stage_probability_map:
            deal.probability = stage_probability_map[new_stage]
        
        # Set close dates if closing
        if new_stage in ['closed_won', 'closed_lost']:
            deal.actual_close_date = timezone.now().date()
            if new_stage == 'closed_lost':
                deal.lost_reason = request.data.get('lost_reason', '')
                deal.lost_notes = request.data.get('lost_notes', '')
        
        deal.save()
        
        serializer = self.get_serializer(deal)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stage_history(self, request, pk=None):
        """Get deal stage change history"""
        deal = self.get_object()
        history = deal.stage_history.all().order_by('-changed_at')
        serializer = DealStageHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Get all tasks for a deal"""
        deal = self.get_object()
        tasks = deal.tasks.filter(is_active=True)
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pipeline(self, request):
        """Get deal pipeline statistics by stage"""
        pipeline = Deal.objects.filter(is_active=True).values(
            'stage'
        ).annotate(
            count=Count('id'),
            total_amount=Sum('amount'),
            weighted_amount=Sum(F('amount') * F('probability') / 100.0)
        ).order_by('stage')
        
        return Response(pipeline)
    
    @action(detail=False, methods=['get'])
    def forecast(self, request):
        """Get sales forecast data"""
        # Get deals expected to close in next 30, 60, 90 days
        today = timezone.now().date()
        
        periods = {
            'next_30_days': today + timedelta(days=30),
            'next_60_days': today + timedelta(days=60),
            'next_90_days': today + timedelta(days=90),
        }
        
        forecast_data = {}
        for period_name, end_date in periods.items():
            deals = Deal.objects.filter(
                is_active=True,
                expected_close_date__range=[today, end_date]
            ).exclude(
                Q(stage='closed_won') | Q(stage='closed_lost')
            )
            
            forecast_data[period_name] = {
                'count': deals.count(),
                'total_amount': deals.aggregate(Sum('amount'))['amount__sum'] or 0,
                'weighted_amount': deals.aggregate(
                    total=Sum(F('amount') * F('probability') / 100.0)
                )['total'] or 0
            }
        
        return Response(forecast_data)


# Task Views
class TaskViewSet(BaseCRUDViewSet):
    """Viewset for Task CRUD operations"""
    model = Task
    search_fields = ['title', 'description', 'contact__first_name', 'contact__last_name', 
                    'deal__title', 'company__name']
    filterset_fields = ['status', 'priority', 'task_type', 'assigned_to', 'is_active']
    ordering_fields = ['due_date', 'priority', 'created_at', 'updated_at']
    ordering = ['priority', 'due_date']
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail"""
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer
    
    def get_queryset(self):
        """Custom queryset with annotations"""
        queryset = super().get_queryset()
        
        # Filter by overdue status
        overdue = self.request.query_params.get('overdue', None)
        if overdue is not None:
            today = timezone.now()
            if overdue.lower() == 'true':
                queryset = queryset.filter(
                    due_date__lt=today,
                    status__in=['pending', 'in_progress']
                )
            elif overdue.lower() == 'false':
                queryset = queryset.exclude(
                    due_date__lt=today,
                    status__in=['pending', 'in_progress']
                )
        
        # Filter by assigned_to
        assigned_to = self.request.query_params.get('assigned_to', None)
        if assigned_to:
            try:
                user_uuid = uuid.UUID(assigned_to)
                queryset = queryset.filter(assigned_to_id=user_uuid)
            except (ValueError, User.DoesNotExist):
                pass
        
        # Filter by due date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(due_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(due_date__date__lte=end_date)
        
        # Filter by completion status
        completed = self.request.query_params.get('completed', None)
        if completed is not None:
            if completed.lower() == 'true':
                queryset = queryset.filter(status='completed')
            elif completed.lower() == 'false':
                queryset = queryset.exclude(status='completed')
        
        # Annotate with overdue status
        today = timezone.now()
        queryset = queryset.annotate(
            is_overdue=Case(
                When(
                    Q(due_date__lt=today) & 
                    Q(status__in=['pending', 'in_progress']),
                    then=True
                ),
                default=False,
                output_field=IntegerField()
            )
        )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a task"""
        task = self.get_object()
        actual_hours = request.data.get('actual_hours')
        notes = request.data.get('notes', '')
        
        task.complete_task(actual_hours, notes)
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reassign(self, request, pk=None):
        """Reassign task to another user"""
        task = self.get_object()
        assigned_to_id = request.data.get('assigned_to_id')
        
        if not assigned_to_id:
            return Response(
                {'error': 'assigned_to_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=assigned_to_id)
            task.assigned_to = user
            task.save()
        except (ValueError, User.DoesNotExist):
            return Response(
                {'error': 'Invalid user ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue tasks"""
        today = timezone.now()
        overdue_tasks = Task.objects.filter(
            is_active=True,
            due_date__lt=today,
            status__in=['pending', 'in_progress']
        ).order_by('due_date')
        
        serializer = TaskListSerializer(overdue_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming tasks (due in next 7 days)"""
        today = timezone.now()
        next_week = today + timedelta(days=7)
        
        upcoming_tasks = Task.objects.filter(
            is_active=True,
            due_date__range=[today, next_week],
            status__in=['pending', 'in_progress']
        ).order_by('due_date')
        
        serializer = TaskListSerializer(upcoming_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks assigned to current user"""
        tasks = Task.objects.filter(
            is_active=True,
            assigned_to=request.user
        ).exclude(status='completed')
        
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)


# Interaction Views
class InteractionViewSet(BaseCRUDViewSet):
    """Viewset for Interaction CRUD operations"""
    model = Interaction
    serializer_class = InteractionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['interaction_type', 'contact', 'company', 'deal', 'is_active']
    ordering_fields = ['interaction_date', 'created_at']
    ordering = ['-interaction_date']
    
    def get_queryset(self):
        """Custom queryset filtering"""
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(interaction_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(interaction_date__date__lte=end_date)
        
        # Filter by entity type
        entity_type = self.request.query_params.get('entity_type', None)
        entity_id = self.request.query_params.get('entity_id', None)
        
        if entity_type and entity_id:
            try:
                entity_uuid = uuid.UUID(entity_id)
                if entity_type == 'contact':
                    queryset = queryset.filter(contact_id=entity_uuid)
                elif entity_type == 'company':
                    queryset = queryset.filter(company_id=entity_uuid)
                elif entity_type == 'deal':
                    queryset = queryset.filter(deal_id=entity_uuid)
            except ValueError:
                pass
        
        return queryset


# Dashboard Views
class DashboardView(generics.GenericAPIView):
    """Dashboard statistics view"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get comprehensive dashboard statistics"""
        user = request.user
        
        # Basic counts
        total_companies = Company.objects.filter(is_active=True).count()
        total_contacts = Contact.objects.filter(is_active=True).count()
        
        # Deal statistics
        deals = Deal.objects.filter(is_active=True)
        total_deals = deals.count()
        
        active_deals = deals.exclude(
            Q(stage='closed_won') | Q(stage='closed_lost')
        )
        active_deals_value = active_deals.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        weighted_deals_value = active_deals.aggregate(
            total=Sum(F('amount') * F('probability') / 100.0)
        )['total'] or 0
        
        # Task statistics
        tasks = Task.objects.filter(is_active=True)
        total_tasks = tasks.count()
        overdue_tasks = tasks.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()
        pending_tasks = tasks.filter(status='pending').count()
        
        # Deal pipeline by stage
        deal_pipeline = dict(Deal.STAGE_CHOICES)
        for stage in deal_pipeline.keys():
            deal_pipeline[stage] = deals.filter(stage=stage).count()
        
        # Recent activities (last 10 of each)
        recent_companies = Company.objects.filter(
            is_active=True
        ).order_by('-created_at')[:10]
        
        recent_contacts = Contact.objects.filter(
            is_active=True
        ).order_by('-created_at')[:10]
        
        recent_deals = Deal.objects.filter(
            is_active=True
        ).order_by('-created_at')[:10]
        
        recent_tasks = Task.objects.filter(
            is_active=True
        ).order_by('-created_at')[:10]
        
        # Monthly deal trend (last 6 months)
        six_months_ago = timezone.now() - timedelta(days=180)
        monthly_deals = deals.filter(
            created_at__gte=six_months_ago
        ).annotate(
            month=ExtractMonth('created_at'),
            year=ExtractYear('created_at')
        ).values('year', 'month').annotate(
            count=Count('id'),
            amount=Sum('amount')
        ).order_by('year', 'month')
        
        # Top companies by deal value
        top_companies = Company.objects.filter(
            is_active=True,
            deals__is_active=True
        ).annotate(
            deal_count=Count('deals'),
            total_deal_value=Sum('deals__amount')
        ).order_by('-total_deal_value')[:5]
        
        data = {
            'total_companies': total_companies,
            'total_contacts': total_contacts,
            'total_deals': total_deals,
            'total_tasks': total_tasks,
            'active_deals_value': active_deals_value,
            'weighted_deals_value': weighted_deals_value,
            'overdue_tasks': overdue_tasks,
            'pending_tasks': pending_tasks,
            'deal_pipeline': deal_pipeline,
            'recent_companies': CompanyListSerializer(recent_companies, many=True).data,
            'recent_contacts': ContactListSerializer(recent_contacts, many=True).data,
            'recent_deals': DealListSerializer(recent_deals, many=True).data,
            'recent_tasks': TaskListSerializer(recent_tasks, many=True).data,
            'monthly_trend': list(monthly_deals),
            'top_companies': CompanyListSerializer(top_companies, many=True).data,
            'user_stats': {
                'assigned_tasks': Task.objects.filter(
                    is_active=True, assigned_to=user
                ).exclude(status='completed').count(),
                'assigned_deals': Deal.objects.filter(
                    is_active=True, assigned_to=user
                ).exclude(
                    Q(stage='closed_won') | Q(stage='closed_lost')
                ).count(),
                'recent_activity': Interaction.objects.filter(
                    is_active=True, created_by=user
                ).count()
            }
        }
        
        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)


# User Profile Views
class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile management view"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSimpleSerializer
    
    def get_object(self):
        return self.request.user


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """Notification preference management view"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationPreferenceSerializer
    
    def get_object(self):
        # Get or create notification preferences for user
        preferences, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preferences


# Utility Views
class BulkDeleteView(generics.GenericAPIView):
    """Bulk delete/soft delete view"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Bulk delete/soft delete items"""
        model_type = request.data.get('model_type')
        ids = request.data.get('ids', [])
        
        if not model_type or not ids:
            return Response(
                {'error': 'model_type and ids are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Map model type to actual model
        model_map = {
            'company': Company,
            'contact': Contact,
            'deal': Deal,
            'task': Task,
            'interaction': Interaction,
        }
        
        if model_type not in model_map:
            return Response(
                {'error': f'Invalid model_type. Valid options: {", ".join(model_map.keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        model = model_map[model_type]
        deleted_count = 0
        
        # Convert string IDs to UUIDs
        try:
            uuid_ids = [uuid.UUID(id_str) for id_str in ids]
        except ValueError:
            return Response(
                {'error': 'Invalid UUID format in ids'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get queryset
        queryset = model.objects.filter(id__in=uuid_ids)
        
        # Check if model supports soft delete
        if hasattr(model, 'soft_delete'):
            for item in queryset:
                item.soft_delete()
                deleted_count += 1
        else:
            deleted_count, _ = queryset.delete()
        
        return Response({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Successfully deleted {deleted_count} items'
        })


class ExportDataView(generics.GenericAPIView):
    """Export data view (CSV, JSON, etc.)"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Export data based on parameters"""
        model_type = request.query_params.get('model_type')
        format_type = request.query_params.get('format', 'json')
        
        if not model_type:
            return Response(
                {'error': 'model_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Map model type to serializer
        serializer_map = {
            'companies': CompanyListSerializer,
            'contacts': ContactListSerializer,
            'deals': DealListSerializer,
            'tasks': TaskListSerializer,
        }
        
        if model_type not in serializer_map:
            return Response(
                {'error': f'Invalid model_type. Valid options: {", ".join(serializer_map.keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get data
        if model_type == 'companies':
            queryset = Company.objects.filter(is_active=True)
        elif model_type == 'contacts':
            queryset = Contact.objects.filter(is_active=True)
        elif model_type == 'deals':
            queryset = Deal.objects.filter(is_active=True)
        elif model_type == 'tasks':
            queryset = Task.objects.filter(is_active=True)
        
        # Apply filters from query params
        queryset = self.apply_filters(queryset, request)
        
        serializer_class = serializer_map[model_type]
        serializer = serializer_class(queryset, many=True)
        
        if format_type == 'csv':
            # Convert to CSV
            import csv
            from django.http import HttpResponse
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{model_type}_export.csv"'
            
            # Write CSV header
            writer = csv.writer(response)
            if serializer.data:
                writer.writerow(serializer.data[0].keys())
                
                # Write data rows
                for row in serializer.data:
                    writer.writerow(row.values())
            
            return response
        
        # Default to JSON
        return Response(serializer.data)
    
    def apply_filters(self, queryset, request):
        """Apply filters from query parameters"""
        # Add your filtering logic here based on model_type
        return queryset
