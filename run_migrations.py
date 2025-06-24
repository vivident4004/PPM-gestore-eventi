import os
import sys
import subprocess
import django
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProgettoEventi.settings')

def main():
    """
    Run database migrations and create a superuser if needed.
    This script can be run locally or in a CI/CD pipeline.
    """
    print("Starting database migrations...")

    # Check if DATABASE_URL is set
    if not os.environ.get('DATABASE_URL'):
        print("ERROR: DATABASE_URL environment variable is not set.")
        print("Please set the DATABASE_URL environment variable to point to your PostgreSQL database.")
        sys.exit(1)

    try:
        # Initialize Django
        django.setup()

        # Run migrations
        print("Applying migrations...")
        subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'], check=True)

        # Set up user groups
        print("Setting up user groups...")
        subprocess.run([sys.executable, 'manage.py', 'setup_groups'], check=True)

        # Create superuser if needed
        print("Creating superuser if needed...")
        subprocess.run([sys.executable, 'manage.py', 'makesu'], check=True)

        print("Database setup completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
