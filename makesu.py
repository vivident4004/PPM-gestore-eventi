import os
import django

# Imposta l'ambiente di Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProgettoEventi.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Ottieni i dettagli del superutente dalle variabili d'ambiente
SUPERUSER_EMAIL = os.environ.get("DJANGO_SUPERUSER_EMAIL")
SUPERUSER_USERNAME = os.environ.get("DJANGO_SUPERUSER_USERNAME")
SUPERUSER_PASSWORD = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

# Procedi solo se tutte le variabili sono state impostate
if SUPERUSER_EMAIL and SUPERUSER_USERNAME and SUPERUSER_PASSWORD:
    if not User.objects.filter(username=SUPERUSER_USERNAME).exists():
        print(f"Creazione del superutente: {SUPERUSER_USERNAME}")
        User.objects.create_superuser(
            username=SUPERUSER_USERNAME,
            email=SUPERUSER_EMAIL,
            password=SUPERUSER_PASSWORD
        )
        print("Superutente creato con successo.")
    else:
        print(f"Il superutente '{SUPERUSER_USERNAME}' esiste già.")
else:
    print("Variabili d'ambiente per il superutente non impostate. Creazione saltata.")
