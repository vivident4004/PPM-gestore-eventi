from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from GestoreEventi.models import Event, Registration

class Command(BaseCommand):
    help = 'Creates user groups and assigns permissions'

    def handle(self, *args, **options):
        # Create groups
        attendee_group, created = Group.objects.get_or_create(name='Attendees')
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created Attendees group'))
        else:
            self.stdout.write(self.style.WARNING('Attendees group already exists'))

        organizer_group, created = Group.objects.get_or_create(name='Organizers')
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created Organizers group'))
        else:
            self.stdout.write(self.style.WARNING('Organizers group already exists'))

        # Get content types
        event_content_type = ContentType.objects.get_for_model(Event)
        registration_content_type = ContentType.objects.get_for_model(Registration)

        # Define permissions for Attendees
        attendee_permissions = [
            # View events
            Permission.objects.get(content_type=event_content_type, codename='view_event'),
            # View own registrations
            Permission.objects.get(content_type=registration_content_type, codename='view_registration'),
            # Register/unregister for events
            Permission.objects.get(content_type=registration_content_type, codename='add_registration'),
            Permission.objects.get(content_type=registration_content_type, codename='delete_registration'),
        ]

        # Define permissions for Organizers (includes all Attendee permissions)
        organizer_permissions = attendee_permissions + [
            # Create, update, delete own events
            Permission.objects.get(content_type=event_content_type, codename='add_event'),
            Permission.objects.get(content_type=event_content_type, codename='change_event'),
            Permission.objects.get(content_type=event_content_type, codename='delete_event'),
        ]

        # Assign permissions to groups
        attendee_group.permissions.set(attendee_permissions)
        self.stdout.write(self.style.SUCCESS('Successfully assigned permissions to Attendees group'))

        organizer_group.permissions.set(organizer_permissions)
        self.stdout.write(self.style.SUCCESS('Successfully assigned permissions to Organizers group'))