# Generated by Django 5.1.4 on 2025-02-04 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timehero', '0004_remove_task_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='difficulty',
            field=models.IntegerField(default=1),
        ),
    ]
