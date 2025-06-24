# Sistema di gestione degli eventi

Questo è un progetto universitario per un'applicazione web in Django per la gestione di eventi, dove gli utenti possono creare, gestire e partecipare a eventi.

## Funzionalità

- Registrazione e autenticazione utente
- Due gruppi di utenti con permessi distinti:
  - **Partecipanti**: Possono visualizzare eventi, registrarsi/cancellare la propria registrazione e vedere le proprie registrazioni
  - **Organizzatori**: Possono fare tutto ciò che fanno i partecipanti, più creare, aggiornare ed eliminare i propri eventi e visualizzare la lista dei partecipanti ai loro eventi
- Creazione, modifica e cancellazione di eventi
- Registrazione a eventi e tracciamento delle partecipazioni
- Design responsivo tramite Bootstrap

## Installazione

1. Clona il repositorio:
   ```
   git clone <url-del-repositorio>
   cd ProgettoEventi
   ```

2. Crea e attiva un ambiente virtuale:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Installa le dipendenze:
   ```
   pip install -r requirements.txt
   ```

4. Imposta le variabili d'ambiente:
   - Copia `.env.example` in `.env`
   - Modifica `.env` per impostare la tua `SECRET_KEY` e altre impostazioni
   ```
   cp .env.example .env
   # Modifica .env con il tuo editor di testo preferito
   ```

5. Applica le migrazioni:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Crea i gruppi utente e imposta i permessi:
   ```
   python manage.py setup_groups
   ```

7. Avvia il server di sviluppo:
   ```
   python manage.py runserver
   ```

8. Accedi all'applicazione all'indirizzo http://127.0.0.1:8000/

## Utilizzo

### Interfaccia di amministrazione

1. Accedi all'interfaccia di amministrazione all'indirizzo http://127.0.0.1:8000/admin/
2. Accedi con le credenziali del superutente create in precedenza
3. Puoi gestire utenti, eventi e registrazioni dall'interfaccia di amministrazione

### Registrazione utente

1. Clicca su "Login" nella barra di navigazione
2. Clicca su "Registrati qui" per creare un nuovo account
3. Compila il modulo di registrazione
   - Seleziona "Registrati come organizzatore di eventi" se vuoi creare eventi
   - Lascia deselezionato se vuoi solo partecipare agli eventi
4. Clicca "Registrati" per creare il tuo account

### Creare eventi (solo organizzatori)

1. Accedi come organizzatore
2. Clicca su "Crea evento" nella barra di navigazione
3. Compila i dettagli dell'evento
4. Clicca "Crea evento" per creare l'evento

### Registrarsi agli eventi

1. Accedi come un qualsiasi utente
2. Sfoglia gli eventi nella pagina principale
3. Clicca "Vedi dettagli" su un evento che ti interessa
4. Clicca "Registrati" per registrarti all'evento
5. Puoi visualizzare le tue registrazioni cliccando "Le mie registrazioni" nella barra di navigazione

### Gestire i tuoi eventi (solo organizzatori)

1. Accedi come organizzatore
2. Vai a un evento che hai creato
3. Vedrai le opzioni per modificare, eliminare o visualizzare i partecipanti all'evento

## Configurazione con docker

Questo progetto può essere eseguito tramite Docker, il che è particolarmente utile per gestire dipendenze come `gettext` per le traduzioni.

### Prerequisiti

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installato sulla tua macchina

### Costruire ed eseguire con docker

1. Costruisci l'immagine Docker:
   ```
   docker-compose build
   ```

2. Avvia il container:
   ```
   docker-compose up -d
   ```

3. Esegui le migrazioni all'interno del container:
   ```
   docker-compose exec web python manage.py migrate
   ```

4. Crea i gruppi utente e imposta i permessi:
   ```
   docker-compose exec web python manage.py setup_groups
   ```

5. Crea un superutente:
   ```
   docker-compose exec web python manage.py createsuperuser
   ```

6. Accedi all'applicazione all'indirizzo http://localhost:8000/

### Lavorare con le traduzioni

Per lavorare con le traduzioni, usa i seguenti comandi all'interno del container Docker:

1. Genera i file dei messaggi per una lingua specifica (es. italiano):
   ```
   docker-compose exec web python manage.py makemessages -l it
   ```

2. Compila i file dei messaggi:
   ```
   docker-compose exec web python manage.py compilemessages
   ```

### Fermare il container

Per fermare il container in esecuzione:
```
docker-compose down
```

## struttura del progetto

- **ProgettoEventi/**: Cartella principale del progetto
  - **GestoreEventi/**: App per la gestione degli eventi
    - **models.py**: Definisce i modelli Event e Registration
    - **views.py**: Contiene le viste per la lista eventi, dettaglio, creazione, ecc.
    - **urls.py**: Pattern URL per l'app
  - **users/**: App per la gestione degli utenti
    - **models.py**: Definisce il modello CustomUser
    - **views.py**: Contiene le viste per la registrazione utente
    - **urls.py**: Pattern URL per l'app
  - **templates/**: Template HTML
    - **base.html**: Template di base con navigazione e layout
    - **GestoreEventi/**: Template per le viste degli eventi
    - **registration/**: Template per le viste di autenticazione
  - **Dockerfile**: Definisce l'immagine Docker per il progetto
  - **docker-compose.yml**: Configura i servizi Docker

## Deployment su Vercel

Questo progetto è configurato per essere facilmente deployato su Vercel. Segui questi passaggi per deployare l'applicazione:

### Prerequisiti

- Un account Vercel
- [Vercel CLI](https://vercel.com/download) installato
- Accesso a un database PostgreSQL (puoi usare servizi come Railway, Supabase, o Neon)

### Configurazione del database

1. Crea un database PostgreSQL su un servizio cloud (Railway, Supabase, Neon, ecc.)
2. Ottieni l'URL di connessione al database

### Deployment

1. Accedi a Vercel CLI:
   ```
   vercel login
   ```

2. Configura le variabili d'ambiente su Vercel utilizzando lo script fornito:
   ```
   sh setup_vercel_env.sh
   ```
   Questo script imposterà automaticamente le seguenti variabili d'ambiente su Vercel:
   - `SECRET_KEY`: La chiave segreta per Django
   - `DEBUG`: Impostato su "False" per l'ambiente di produzione
   - `DATABASE_URL`: L'URL di connessione al database PostgreSQL

3. Esegui il deployment:
   ```
   vercel --prod
   ```

4. Segui le istruzioni a schermo. Quando richiesto:
   - Conferma la directory del progetto
   - Conferma che è un progetto Django
   - Configura le impostazioni di build se necessario

5. Una volta completato il deployment, esegui le migrazioni del database:

   ```
   python run_migrations.py
   ```

   Questo script verificherà che DATABASE_URL sia impostato, eseguirà le migrazioni e creerà un superuser se necessario.

   Nota: Questo script deve essere eseguito localmente o tramite un servizio CI/CD come GitHub Actions, poiché Vercel non supporta l'esecuzione diretta di script Python dopo il deployment.

6. Accedi all'URL fornito da Vercel per visualizzare la tua applicazione

### Aggiornamenti

Per aggiornare l'applicazione dopo aver apportato modifiche:

1. Esegui nuovamente il deployment:
   ```
   vercel
   ```

2. Se hai apportato modifiche al database, puoi utilizzare il workflow GitHub Actions incluso:

   Questo progetto include un workflow GitHub Actions (`.github/workflows/vercel-deploy.yml`) che automatizza il processo di deployment e l'esecuzione delle migrazioni del database.

   Per utilizzarlo:

   a. Configura i seguenti secrets nel tuo repository GitHub:
      - `VERCEL_TOKEN`: Il tuo token API Vercel (ottenibile da https://vercel.com/account/tokens)
      - `DATABASE_URL`: L'URL di connessione al tuo database PostgreSQL
      - `SECRET_KEY`: La chiave segreta per Django

   b. Esegui il push del codice sul branch main o avvia manualmente il workflow dalla sezione Actions del tuo repository GitHub.

   Il workflow si occuperà di:
   - Deployare l'applicazione su Vercel
   - Eseguire le migrazioni del database
   - Creare un superuser se necessario

## Licenza

Questo progetto è rilasciato sotto licenza libera.
