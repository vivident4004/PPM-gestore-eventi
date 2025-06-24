import os
import sys
from django.core.management.base import BaseCommand
from GestoreEventi.models import Event
from GestoreEventi.utils import upload_to_vercel_blob
from django.core.files.uploadedfile import SimpleUploadedFile

class Command(BaseCommand):
    help = 'Migrate local images to Vercel Blob storage'

    def handle(self, *args, **options):
        # Check if Vercel Blob token is configured
        if not os.environ.get('BLOB_READ_WRITE_TOKEN'):
            self.stderr.write(self.style.ERROR("Error: BLOB_READ_WRITE_TOKEN environment variable is not set"))
            return

        # Get all events with images
        events_with_images = Event.objects.exclude(image__exact='').exclude(image__isnull=True)
        self.stdout.write(f"Found {events_with_images.count()} events with images")

        # Process each event
        migrated_count = 0
        skipped_count = 0
        error_count = 0

        for event in events_with_images:
            try:
                # Skip if the image is already a URL
                if event.image and isinstance(event.image, str) and event.image.startswith('http'):
                    self.stdout.write(f"Skipping event {event.id}: Image is already a URL")
                    skipped_count += 1
                    continue
import os
import sys
from django.core.management.base import BaseCommand
from GestoreEventi.models import Event
from GestoreEventi.utils import upload_to_vercel_blob
from django.core.files.uploadedfile import SimpleUploadedFile

class Command(BaseCommand):
    help = 'Migrate local images to Vercel Blob storage'

    def handle(self, *args, **options):
        # Check if Vercel Blob token is configured
        if not os.environ.get('BLOB_READ_WRITE_TOKEN'):
            self.stderr.write(self.style.ERROR("Error: BLOB_READ_WRITE_TOKEN environment variable is not set"))
            return

        # Get all events with images
        events_with_images = Event.objects.exclude(image__exact='').exclude(image__isnull=True)
        self.stdout.write(f"Found {events_with_images.count()} events with images")

        # Process each event
        migrated_count = 0
        skipped_count = 0
        error_count = 0

        for event in events_with_images:
            try:
                # Skip if the image is already a URL
                if event.image and isinstance(event.image, str) and event.image.startswith('http'):
                    self.stdout.write(f"Skipping event {event.id}: Image is already a URL")
                    skipped_count += 1
                    continue

                # Handle both old ImageField and new URLField cases
                if hasattr(event.image, 'path'):
                    # This is still an ImageField (old data)
                    image_path = event.image.path
                    if not os.path.exists(image_path):
                        self.stdout.write(self.style.WARNING(f"Skipping event {event.id}: Image file not found"))
                        skipped_count += 1
                        continue

                    self.stdout.write(f"Processing event {event.id}: {event.title}")

                    # Open the image file
                    with open(image_path, 'rb') as f:
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
                                self.stdout.write(self.style.SUCCESS(
                                    f"  Updated event {event.id} with Vercel Blob URL: {image_url}"))
                                migrated_count += 1
                            else:
                                self.stdout.write(self.style.ERROR(
                                    f"  Failed to upload image for event {event.id}: No URL returned"))
                                error_count += 1
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(
                                f"  Error uploading image for event {event.id}: {str(e)}"))
                            error_count += 1
                else:
                    self.stdout.write(f"Skipping event {event.id}: Not a file-based image")
                    skipped_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing event {event.id}: {str(e)}"))
                error_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Migration completed: {migrated_count} migrated, {skipped_count} skipped, {error_count} errors"))
                # Handle both old ImageField and new URLField cases
                if hasattr(event.image, 'path'):
                    # This is still an ImageField (old data)
                    image_path = event.image.path
                    if not os.path.exists(image_path):
                        self.stdout.write(self.style.WARNING(f"Skipping event {event.id}: Image file not found"))
                        skipped_count += 1
                        continue

                    self.stdout.write(f"Processing event {event.id}: {event.title}")

                    # Open the image file
                    with open(image_path, 'rb') as f:
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
                                self.stdout.write(self.style.SUCCESS(
                                    f"  Updated event {event.id} with Vercel Blob URL: {image_url}"))
                                migrated_count += 1
                            else:
                                self.stdout.write(self.style.ERROR(
                                    f"  Failed to upload image for event {event.id}: No URL returned"))
                                error_count += 1
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(
                                f"  Error uploading image for event {event.id}: {str(e)}"))
                            error_count += 1
                else:
                    self.stdout.write(f"Skipping event {event.id}: Not a file-based image")
                    skipped_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing event {event.id}: {str(e)}"))
                error_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Migration completed: {migrated_count} migrated, {skipped_count} skipped, {error_count} errors"))
