import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProgettoEventi.settings')
django.setup()

# Now we can import Django models
from GestoreEventi.models import Event

# Get all events with images
events_with_images = Event.objects.filter(is_deleted=False).exclude(image='').exclude(image=None)

print(f"Found {events_with_images.count()} events with images:")
for event in events_with_images:
    print(f"Event ID: {event.id}, Title: {event.title}, Image: {event.image}")
