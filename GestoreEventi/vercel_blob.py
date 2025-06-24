import os
import json
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from urllib.parse import urlparse

@deconstructible
class VercelBlobStorage(Storage):
    """Custom storage backend for Vercel Blob storage."""

    def __init__(self):
        self.blob_read_write_token = os.environ.get('BLOB_READ_WRITE_TOKEN', '')
        if not self.blob_read_write_token:
            raise ValueError('BLOB_READ_WRITE_TOKEN environment variable is not set')

    def _save(self, name, content):
        """Save a file to Vercel Blob storage."""
        content.seek(0)
        file_content = content.read()

        headers = {
            'Authorization': f'Bearer {self.blob_read_write_token}',
            'Content-Type': 'application/octet-stream',
        }

        # Get the file extension
        _, ext = os.path.splitext(name)

        # Upload to Vercel Blob
        response = requests.put(
            'https://blob.vercel-storage.com/upload',
            headers=headers,
            data=file_content
        )

        if response.status_code != 200:
            raise Exception(f'Failed to upload file to Vercel Blob: {response.text}')

        # Get the URL from the response
        data = response.json()

        # Store the blob URL in the database
        return data['url']

    def _open(self, name, mode='rb'):
        """Open a file from Vercel Blob storage."""
        # For Vercel Blob, we don't need to open the file locally
        # since we just store the URL in the database
        return ContentFile(b'')

    def url(self, name):
        """Return the URL for accessing the file."""
        # For Vercel Blob, the name is already the full URL
        return name

    def delete(self, name):
        """Delete a file from Vercel Blob storage."""
        if not name or not name.startswith('https://'):  # Basic validation
            return

        headers = {
            'Authorization': f'Bearer {self.blob_read_write_token}',
            'Content-Type': 'application/json',
        }

        # Extract the blob URL from the full URL
        try:
            # Make the deletion request
            response = requests.delete(
                'https://blob.vercel-storage.com/delete',
                headers=headers,
                json={'url': name}
            )

            if response.status_code != 200:
                raise Exception(f'Failed to delete file from Vercel Blob: {response.text}')
        except Exception as e:
            # Log the error but don't raise it to prevent breaking the application
            print(f'Error deleting file from Vercel Blob: {e}')

    def exists(self, name):
        """Check if a file exists in Vercel Blob storage."""
        if not name or not name.startswith('https://'):  # Basic validation
            return False

        try:
            response = requests.head(name, timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_available_name(self, name, max_length=None):
        """Return a filename that's free on the target storage system."""
        # For Vercel Blob, we don't need to check for file existence
        # since each upload generates a unique URL
        return name
