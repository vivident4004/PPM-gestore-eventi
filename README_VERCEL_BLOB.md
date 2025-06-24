# Vercel Blob Integration for Django

## Overview

This project uses Vercel Blob for storing and serving images. Vercel Blob is a scalable, global object storage service for media files.

## Setup Instructions

### 1. Set Environment Variable

You need to set the `BLOB_READ_WRITE_TOKEN` environment variable:

#### On Windows (Command Prompt):

```cmd
set BLOB_READ_WRITE_TOKEN=your_token_here
```

#### On Windows (PowerShell):

```powershell
$env:BLOB_READ_WRITE_TOKEN = "your_token_here"
```

#### For PyCharm:

In PyCharm, you can set environment variables in your run configuration:

1. Go to Run > Edit Configurations
2. Select your Django server configuration
3. In the "Environment variables" field, add: `BLOB_READ_WRITE_TOKEN=your_token_here`
4. Click OK to save

### 2. Getting a Vercel Blob Token

1. Create a Vercel account if you don't have one
2. Create a new project or use an existing one
3. Go to the Storage tab in your Vercel dashboard
4. Create a new Blob store
5. Generate a new token with read/write permissions

### 3. Migrate Existing Images

To migrate existing images from the local filesystem to Vercel Blob:

```cmd
python manage.py migrate_to_vercel_blob
```

## How It Works

- Images are uploaded directly to Vercel Blob from the browser
- The URL of the uploaded image is stored in the database
- Images are served directly from Vercel's global CDN

## Troubleshooting

### Common Issues

1. **Missing Environment Variable**: Ensure the `BLOB_READ_WRITE_TOKEN` is set in your environment

2. **Invalid Token**: Verify your token has the correct permissions (read/write)

3. **Upload Failures**: Check your network connectivity and the size of the images you're uploading

### Debugging

If you encounter issues with Vercel Blob uploads, check the Django error logs for detailed error messages.
