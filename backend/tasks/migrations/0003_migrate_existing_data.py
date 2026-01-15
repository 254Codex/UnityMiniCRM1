
# backend/tasks/migrations/0003_migrate_existing_data.py

from django.db import migrations
import uuid
from django.utils import timezone


def migrate_existing_data(apps, schema_editor):
    """
    This is an optional migration to transfer data from old models if they exist.
    Since you're replacing models, you likely don't have data to migrate.
    """
    print("No existing data to migrate. Starting fresh with enhanced models.")


def reverse_migration(apps, schema_editor):
    """Reverse migration - nothing to do since we're not keeping old data"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_supporting_models'),
    ]

    operations = [
        migrations.RunPython(migrate_existing_data, reverse_migration),
    ]
