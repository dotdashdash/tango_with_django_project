# Generated by Django 5.1.4 on 2025-03-09 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timehero', '0010_remove_user_tasks_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='tasks_completed',
            field=models.IntegerField(default=0),
        ),
    ]
