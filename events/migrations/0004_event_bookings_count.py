# Generated by Django 5.1 on 2024-09-09 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='bookings_count',
            field=models.IntegerField(default=0),
        ),
    ]
