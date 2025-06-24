import os
import requests
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

def upload_to_vercel_blob(file_obj):
    """
    Upload a file to Vercel Blob and return the URL.

    Args:
        file_obj: An uploaded file object (InMemoryUploadedFile or TemporaryUploadedFile)

    Returns:
        str: The URL of the uploaded file in Vercel Blob
    """
    if not file_obj:
        return None

    if not isinstance(file_obj, (InMemoryUploadedFile, TemporaryUploadedFile)):
        raise ValueError(f"Unsupported file object type: {type(file_obj)}")

    # Get the Vercel Blob token from environment variables
    blob_token = os.environ.get('BLOB_READ_WRITE_TOKEN')
    if not blob_token:
        raise ValueError('BLOB_READ_WRITE_TOKEN environment variable is not set')

    # Set up the headers for the request
    headers = {
        'Authorization': f'Bearer {blob_token}',
    }

    # Read the file content
    file_obj.seek(0)
    file_content = file_obj.read()

    # Upload the file to Vercel Blob
    response = requests.post(
        'https://blob.vercel-storage.com/upload',
        headers=headers,
        files={'file': (file_obj.name, file_content)}
    )

    # Check if the upload was successful
    if response.status_code != 200:
        raise Exception(f'Failed to upload file to Vercel Blob: {response.text}')

    # Parse the response to get the URL
    response_data = response.json()
    return response_data.get('url')

def delete_from_vercel_blob(url):
    """
    Delete a file from Vercel Blob.

    Args:
        url (str): The URL of the file to delete

    Returns:
        bool: True if the deletion was successful, False otherwise
    """
    if not url or not url.startswith('https://'):
        return False

    # Get the Vercel Blob token from environment variables
    blob_token = os.environ.get('BLOB_READ_WRITE_TOKEN')
    if not blob_token:
        raise ValueError('BLOB_READ_WRITE_TOKEN environment variable is not set')

    # Set up the headers for the request
    headers = {
        'Authorization': f'Bearer {blob_token}',
        'Content-Type': 'application/json',
    }

    try:
        # Delete the file from Vercel Blob
        response = requests.delete(
            'https://blob.vercel-storage.com/delete',
            headers=headers,
            json={'url': url}
        )

        # Check if the deletion was successful
        return response.status_code == 200
    except Exception:
        return False
