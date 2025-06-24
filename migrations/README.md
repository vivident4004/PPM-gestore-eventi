# Migration Scripts

## Vercel Blob Migration

This project has been updated to use Vercel Blob for image storage.

### Using the Management Command

**Prerequisites:**

1. Make sure you have set up your `BLOB_READ_WRITE_TOKEN` environment variable.
2. Ensure all dependencies are installed: `pip install -r requirements.txt`

**Usage on Windows:**

```cmd
python manage.py migrate_to_vercel_blob
```

**What this command does:**

1. Finds all events that have images stored in the local filesystem
2. For each image, uploads it to Vercel Blob
3. Updates the event record with the new Vercel Blob URL

**Note:** This command is idempotent - it will skip images that are already URLs.
