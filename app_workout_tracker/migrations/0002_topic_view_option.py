# Generated by Django 3.1.3 on 2021-01-02 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_workout_tracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='view_option',
            field=models.BooleanField(default=True),
        ),
    ]
