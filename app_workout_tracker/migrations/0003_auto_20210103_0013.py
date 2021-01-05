# Generated by Django 3.1.3 on 2021-01-03 05:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_workout_tracker', '0002_topic_view_option'),
    ]

    operations = [
        migrations.RenameField(
            model_name='goal',
            old_name='goal_summary',
            new_name='summary',
        ),
        migrations.RenameField(
            model_name='goal',
            old_name='goal_text',
            new_name='text',
        ),
        migrations.RenameField(
            model_name='mistake',
            old_name='mistake_summary',
            new_name='summary',
        ),
        migrations.RenameField(
            model_name='mistake',
            old_name='mistake_text',
            new_name='text',
        ),
        migrations.RenameField(
            model_name='progress',
            old_name='progress_summary',
            new_name='summary',
        ),
        migrations.RenameField(
            model_name='progress',
            old_name='progress_text',
            new_name='text',
        ),
    ]