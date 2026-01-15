
# backend/tasks/migrations/0002_supporting_models.py

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial_enhanced_models'),
    ]

    operations = [
        # Create Interaction model
        migrations.CreateModel(
            name='Interaction',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('deleted_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('interaction_type', models.CharField(choices=[('call', 'Phone Call'), ('email', 'Email'), ('meeting', 'Meeting'), ('note', 'Note'), ('demo', 'Product Demo'), ('proposal', 'Proposal Sent')], max_length=20)),
                ('subject', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('interaction_date', models.DateTimeField(db_index=True)),
                ('duration_minutes', models.PositiveIntegerField(blank=True, null=True)),
                ('requires_follow_up', models.BooleanField(default=False)),
                ('follow_up_date', models.DateTimeField(blank=True, null=True)),
                ('follow_up_notes', models.TextField(blank=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='tasks.company')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='tasks.contact')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interactions', to='auth.user')),
                ('deal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='tasks.deal')),
            ],
            options={
                'ordering': ['-interaction_date'],
                'indexes': [
                    models.Index(fields=['interaction_date', 'interaction_type'], name='tasks_inter_interac_33f012_idx'),
                    models.Index(fields=['contact', 'company', 'deal'], name='tasks_inter_contact_4a4496_idx'),
                ],
            },
        ),
        
        # Create DealStageHistory model
        migrations.CreateModel(
            name='DealStageHistory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('from_stage', models.CharField(choices=[('lead', 'Lead'), ('qualified', 'Qualified'), ('proposal', 'Proposal'), ('negotiation', 'Negotiation'), ('closed_won', 'Closed Won'), ('closed_lost', 'Closed Lost'), ('on_hold', 'On Hold')], max_length=20)),
                ('to_stage', models.CharField(choices=[('lead', 'Lead'), ('qualified', 'Qualified'), ('proposal', 'Proposal'), ('negotiation', 'Negotiation'), ('closed_won', 'Closed Won'), ('closed_lost', 'Closed Lost'), ('on_hold', 'On Hold')], max_length=20)),
                ('changed_at', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True)),
                ('changed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
                ('deal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stage_history', to='tasks.deal')),
            ],
            options={
                'verbose_name_plural': 'Deal Stage Histories',
                'ordering': ['-changed_at'],
            },
        ),
        
        # Create NotificationPreference model
        migrations.CreateModel(
            name='NotificationPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_deal_updates', models.BooleanField(default=True)),
                ('email_task_reminders', models.BooleanField(default=True)),
                ('email_weekly_digest', models.BooleanField(default=True)),
                ('in_app_new_assignment', models.BooleanField(default=True)),
                ('in_app_deadline_reminder', models.BooleanField(default=True)),
                ('in_app_team_updates', models.BooleanField(default=True)),
                ('digest_frequency', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default='weekly', max_length=20)),
                ('quiet_hours_start', models.TimeField(blank=True, null=True)),
                ('quiet_hours_end', models.TimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_preferences', to='auth.user')),
            ],
        ),
    ]
