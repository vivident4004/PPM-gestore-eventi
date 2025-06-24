#!/bin/sh
# Exit on error
set -e

echo "Setting up Vercel environment variables..."

# Extract DATABASE_URL from .env file
DATABASE_URL=$(grep DATABASE_URL .env | cut -d= -f2-)

# Set environment variables in Vercel
echo "Setting DATABASE_URL in Vercel..."
vercel env add DATABASE_URL "$DATABASE_URL" --yes

echo "Setting SECRET_KEY in Vercel..."
SECRET_KEY=$(grep SECRET_KEY .env | cut -d= -f2-)
vercel env add SECRET_KEY "$SECRET_KEY" --yes

echo "Setting DEBUG in Vercel..."
DEBUG=$(grep DEBUG .env | cut -d= -f2-)
vercel env add DEBUG "$DEBUG" --yes

echo "Setting BLOB_STORE_ID in Vercel..."
BLOB_STORE_ID=$(grep BLOB_STORE_ID .env | cut -d= -f2-)
vercel env add BLOB_STORE_ID "$BLOB_STORE_ID" --yes

echo "Setting BLOB_API_TOKEN in Vercel..."
BLOB_API_TOKEN=$(grep BLOB_API_TOKEN .env | cut -d= -f2-)
vercel env add BLOB_API_TOKEN "$BLOB_API_TOKEN" --yes
BLOB_READ_WRITE_TOKEN="vercel_blob_rw_YLEEp4rur6YxHL1n_51nFVgBklQvDRluQwmSmp5HJHYkZmb"
vercel env add BLOB_API_TOKEN "vercel_blob_rw_YLEEp4rur6YxHL1n_51nFVgBklQvDRluQwmSmp5HJHYkZmb" --yes
echo "Environment variables set successfully!"
echo "Now run 'vercel --prod' to deploy your application with the new environment variables."
