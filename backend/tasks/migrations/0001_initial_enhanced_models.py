
# backend/tasks/migrations/0001_initial_enhanced_models.py

from django.db import migrations, models
import django.db.models.deletion
import uuid
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        # Create Company model
        migrations.CreateModel(
            name='Company',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('deleted_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=200)),
                ('industry', models.CharField(choices=[('technology', 'Technology'), ('finance', 'Finance'), ('healthcare', 'Healthcare'), ('education', 'Education'), ('retail', 'Retail'), ('manufacturing', 'Manufacturing'), ('consulting', 'Consulting'), ('other', 'Other')], db_index=True, default='other', max_length=50)),
                ('company_size', models.CharField(blank=True, choices=[('micro', 'Micro (1-9)'), ('small', 'Small (10-49)'), ('medium', 'Medium (50-249)'), ('large', 'Large (250+)')], max_length=20, null=True)),
                ('website', models.URLField(blank=True, max_length=500, validators=[django.core.validators.URLValidator(schemes=['http', 'https'])])),
                ('phone', models.CharField(blank=True, help_text='Format: +1234567890', max_length=20)),
                ('email', models.EmailField(blank=True, db_index=True, max_length=254)),
                ('address', models.TextField(blank=True)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('state', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('postal_code', models.CharField(blank=True, max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('tags', models.CharField(blank=True, help_text='Comma-separated tags for categorization', max_length=500)),
                ('annual_revenue', models.DecimalField(blank=True, decimal_places=2, help_text='Annual revenue in USD', max_digits=15, null=True)),
                ('founded_year', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1800), django.core.validators.MaxValueValidator(2100)])),
                ('assigned_to', models.ForeignKey(blank=True, help_text='Primary account manager', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_companies', to='auth.user')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='companies', to='auth.user')),
            ],
            options={
                'verbose_name_plural': 'Companies',
                'ordering': ['-created_at', 'name'],
                'indexes': [
                    models.Index(fields=['name', 'industry'], name='tasks_compa_name_9e0b98_idx'),
                    models.Index(fields=['created_at'], name='tasks_compa_created_45658a_idx'),
                    models.Index(fields=['email'], name='tasks_compa_email_ab67b8_idx'),
                ],
                'constraints': [
                    models.UniqueConstraint(
                        condition=models.Q(('email__isnull', False), ('email__gt', '')),
                        fields=['name', 'email'],
                        name='unique_company_name_email'
                    ),
                ],
            },
        ),
        
        # Create Contact model
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('deleted_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('salutation', models.CharField(blank=True, choices=[('mr', 'Mr.'), ('mrs', 'Mrs.'), ('ms', 'Ms.'), ('dr', 'Dr.'), ('prof', 'Prof.')], max_length=10)),
                ('first_name', models.CharField(db_index=True, max_length=100)),
                ('last_name', models.CharField(db_index=True, max_length=100)),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, help_text='Format: +1234567890', max_length=20)),
                ('mobile', models.CharField(blank=True, help_text='Mobile phone number', max_length=20)),
                ('position', models.CharField(blank=True, db_index=True, max_length=100)),
                ('department', models.CharField(blank=True, max_length=100)),
                ('source', models.CharField(choices=[('website', 'Website'), ('referral', 'Referral'), ('conference', 'Conference'), ('social', 'Social Media'), ('cold_call', 'Cold Call'), ('other', 'Other')], db_index=True, default='other', max_length=50)),
                ('is_decision_maker', models.BooleanField(default=False)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('tags', models.CharField(blank=True, help_text='Comma-separated tags for categorization', max_length=500)),
                ('social_linkedin', models.URLField(blank=True, max_length=500)),
                ('social_twitter', models.URLField(blank=True, max_length=500)),
                ('assigned_to', models.ForeignKey(blank=True, help_text='Primary relationship manager', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_contacts', to='auth.user')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contacts', to='tasks.company')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contacts', to='auth.user')),
            ],
            options={
                'ordering': ['-created_at', 'last_name', 'first_name'],
                'indexes': [
                    models.Index(fields=['last_name', 'first_name'], name='tasks_conta_last_na_9ee1c3_idx'),
                    models.Index(fields=['email'], name='tasks_conta_email_b42144_idx'),
                    models.Index(fields=['company', 'position'], name='tasks_conta_company_6c2d9e_idx'),
                    models.Index(fields=['created_at'], name='tasks_conta_created_a28c50_idx'),
                ],
                'constraints': [
                    models.UniqueConstraint(
                        condition=models.Q(('company__isnull', False)),
                        fields=['email', 'company'],
                        name='unique_contact_email_company'
                    ),
                ],
            },
        ),
        
        # Create Deal model
        migrations.CreateModel(
            name='Deal',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('deleted_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('deal_code', models.CharField(db_index=True, help_text='Unique deal identifier (e.g., DEAL-2024-001)', max_length=50, unique=True)),
                ('title', models.CharField(db_index=True, max_length=200)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(0)])),
                ('currency', models.CharField(choices=[('USD', 'US Dollar'), ('EUR', 'Euro'), ('GBP', 'British Pound'), ('JPY', 'Japanese Yen'), ('CAD', 'Canadian Dollar')], default='USD', max_length=3)),
                ('stage', models.CharField(choices=[('lead', 'Lead'), ('qualified', 'Qualified'), ('proposal', 'Proposal'), ('negotiation', 'Negotiation'), ('closed_won', 'Closed Won'), ('closed_lost', 'Closed Lost'), ('on_hold', 'On Hold')], db_index=True, default='lead', max_length=20)),
                ('probability', models.IntegerField(default=0, help_text='Win probability (0-100%)', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('expected_close_date', models.DateField(blank=True, db_index=True, null=True)),
                ('actual_close_date', models.DateField(blank=True, null=True)),
                ('lost_reason', models.CharField(blank=True, choices=[('price', 'Price'), ('competitor', 'Competitor'), ('timing', 'Timing'), ('features', 'Missing Features'), ('other', 'Other')], max_length=50)),
                ('lost_notes', models.TextField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('tags', models.CharField(blank=True, max_length=500)),
                ('last_contact_date', models.DateField(blank=True, null=True)),
                ('next_follow_up', models.DateField(blank=True, null=True)),
                ('forecast_category', models.CharField(choices=[('pipeline', 'Pipeline'), ('best_case', 'Best Case'), ('commit', 'Commit'), ('closed', 'Closed')], default='pipeline', max_length=50)),
                ('assigned_to', models.ForeignKey(help_text='Primary sales representative', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_deals', to='auth.user')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deals', to='tasks.company')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deals', to='tasks.contact')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_deals', to='auth.user')),
            ],
            options={
                'ordering': ['-created_at', '-expected_close_date'],
                'indexes': [
                    models.Index(fields=['deal_code'], name='tasks_deal_deal_co_6d8af5_idx'),
                    models.Index(fields=['stage', 'expected_close_date'], name='tasks_deal_stage_8a6f1f_idx'),
                    models.Index(fields=['company', 'stage'], name='tasks_deal_company_7aa998_idx'),
                    models.Index(fields=['assigned_to', 'stage'], name='tasks_deal_assign_7a36d5_idx'),
                    models.Index(fields=['probability'], name='tasks_deal_probabi_31f7e6_idx'),
                ],
            },
        ),
        
        # Create Task model
        migrations.CreateModel(
            name='Task',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('deleted_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(db_index=True, max_length=200)),
                ('description', models.TextField(blank=True)),
                ('task_type', models.CharField(choices=[('call', 'Phone Call'), ('email', 'Email'), ('meeting', 'Meeting'), ('follow_up', 'Follow Up'), ('document', 'Document'), ('other', 'Other')], db_index=True, default='other', max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('deferred', 'Deferred')], db-index=True, default='pending', max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], db_index=True, default='medium', max_length=10)),
                ('due_date', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('completed_date', models.DateTimeField(blank=True, null=True)),
                ('estimated_hours', models.DecimalField(blank=True, decimal_places=2, help_text='Estimated hours to complete', max_digits=5, null=True)),
                ('actual_hours', models.DecimalField(blank=True, decimal_places=2, help_text='Actual hours spent', max_digits=5, null=True)),
                ('recurrence_pattern', models.CharField(blank=True, help_text='Cron-like pattern for recurring tasks', max_length=100)),
                ('tags', models.CharField(blank=True, max_length=500)),
                ('attachment', models.FileField(blank=True, help_text='Related file attachment', null=True, upload_to='task_attachments/')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tasks', to='auth.user')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='tasks.company')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='tasks.contact')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_tasks', to='auth.user')),
                ('deal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='tasks.deal')),
                ('parent_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subtasks', to='tasks.task')),
            ],
            options={
                'ordering': ['priority', 'due_date', '-created_at'],
                'indexes': [
                    models.Index(fields=['due_date', 'priority'], name='tasks_task_due_dat_d2a147_idx'),
                    models.Index(fields=['assigned_to', 'status'], name='tasks_task_assign_37c921_idx'),
                    models.Index(fields=['contact', 'deal', 'company'], name='tasks_task_contact_8c5d97_idx'),
                    models.Index(fields=['status', 'completed_date'], name='tasks_task_status_226677_idx'),
                ],
                'permissions': [
                    ('can_reassign_task', 'Can reassign tasks to other users'),
                    ('can_close_task', 'Can close completed tasks'),
                    ('can_view_all_tasks', 'Can view all tasks regardless of assignment'),
                ],
            },
        ),
        
        # Create Deal team_members ManyToMany relationship
        migrations.AddField(
            model_name='deal',
            name='team_members',
            field=models.ManyToManyField(blank=True, help_text='Additional team members working on this deal', related_name='team_deals', to='auth.user'),
        ),
    ]
