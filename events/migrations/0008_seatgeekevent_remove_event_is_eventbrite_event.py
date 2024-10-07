# Generated by Django 5.1 on 2024-09-25 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_event_is_eventbrite_event'),
    ]

    operations = [
        migrations.CreateModel(
            name='SeatGeekEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.CharField(max_length=255, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('datetime_local', models.DateTimeField()),
                ('venue_name', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('url', models.URLField()),
            ],
        ),
        migrations.RemoveField(
            model_name='event',
            name='is_eventbrite_event',
        ),
    ]
