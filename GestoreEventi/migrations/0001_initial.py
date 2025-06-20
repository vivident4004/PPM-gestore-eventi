from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency('users.CustomUser'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('date', models.DateTimeField()),
                ('location', models.CharField(max_length=200)),
                ('max_attendees', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organized_events', to='users.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registered_at', models.DateTimeField(auto_now_add=True)),
                ('attendee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_registrations', to='users.customuser')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GestoreEventi.event')),
            ],
            options={
                'unique_together': {('event', 'attendee')},
            },
        ),
    ]