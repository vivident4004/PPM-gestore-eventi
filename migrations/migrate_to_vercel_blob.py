#!/usr/bin/env python
"""
Migration script to convert existing images to Vercel Blob storage.

This script will:
1. Locate all events with local images
2. Upload each image to Vercel Blob
3. Update the event's image field with the new URL

Usage:
    python manage.py shell < migrations/migrate_to_vercel_blob.py
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProgettoEventi.settings')
django.setup()

# Import required modules
from GestoreEventi.models import Event
from GestoreEventi.utils import upload_to_vercel_blob
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files import File
import requests
import io

# Check if Vercel Blob token is configured
if not os.environ.get('BLOB_READ_WRITE_TOKEN'):
    print("Error: BLOB_READ_WRITE_TOKEN environment variable is not set")
    sys.exit(1)

# Get all events with images
events_with_images = Event.objects.exclude(image__exact='').exclude(image__isnull=True)
print(f"Found {events_with_images.count()} events with images")

# Process each event
for event in events_with_images:
    try:
        # Skip if the image is already a URL
        if event.image and event.image.startswith('http'):
            print(f"Skipping event {event.id}: Image is already a URL")
            continue

        # Get the image path
        image_path = event.image.path if hasattr(event.image, 'path') else None
        if not image_path or not os.path.exists(image_path):
            print(f"Skipping event {event.id}: Image file not found")
            continue

        print(f"Processing event {event.id}: {event.title}")

        # Open the image file
        with open(image_path, 'rb') as f:
            # Create a file-like object that can be uploaded
            from django.core.files.uploadedfile import SimpleUploadedFile
            file_name = os.path.basename(image_path)
            file_content = f.read()
            file_obj = SimpleUploadedFile(file_name, file_content)

            # Upload to Vercel Blob
            try:
                image_url = upload_to_vercel_blob(file_obj)
                if image_url:
                    # Update the event with the new URL
                    event.image = image_url
                    event.save(update_fields=['image'])
                    print(f"  Updated event {event.id} with Vercel Blob URL: {image_url}")
                else:
                    print(f"  Failed to upload image for event {event.id}: No URL returned")
            except Exception as e:
                print(f"  Error uploading image for event {event.id}: {str(e)}")
    except Exception as e:
        print(f"Error processing event {event.id}: {str(e)}")

print("Migration completed")
