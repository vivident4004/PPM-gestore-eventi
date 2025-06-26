# Sistema di gestione degli eventi

Questo è un progetto universitario per un'applicazione web in Django per la gestione di eventi, dove gli utenti possono visualizzare, creare, gestire e partecipare a eventi.
Il sito è visitabile alla pagina https://progetto-eventi-seven.vercel.app ![Live](https://img.shields.io/badge/status-live-success)

## Funzionalità

- Registrazione e autenticazione utente
- Due gruppi di utenti con permessi distinti:
  - **Partecipanti**: possono visualizzare eventi, registrarsi/cancellare la propria registrazione e vedere le proprie registrazioni
  - **Organizzatori**: possono fare tutto ciò che fanno i partecipanti, più creare, aggiornare ed eliminare i propri eventi e visualizzare la lista dei partecipanti ai loro eventi
- Creazione, modifica e cancellazione di eventi, con anche vista a calendario
- Registrazione a eventi e tracciamento delle partecipazioni
- Pannello di controllo utente
- Categorie, caricamento d'immagini filtri per prezzo, ricerca globale intelligente
- Sito bilingue completamente tradotto
- Design responsivo tramite Bootstrap

## Installazione

1. Clona il repositorio:
   ```
   git clone https://github.com/vivident4004/PPM-gestore-eventi
   cd PPM-gestore-eventi
   ```

2. Crea e attiva un ambiente virtuale nella cartella del progetto:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Nel docker-compose.yml inserisci un valore per SECRET_KEY, oppure inserisci tale parametro nel documento ```.env```.
(su GNU/Linux e altri sistemi operativi i comandi per attivare l'ambiente virtuale potrebbero essere diversi. Consulta [questa pagina](https://docs.python.org/3/library/venv.html#how-venvs-work) per trovare il comando giusto per te. Ad esempio, su Ubuntu il comando è ```source .venv/bin/activate```.)

### Costruzione ed esecuzione con Docker
### Prerequisiti

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installato sulla macchina e in esecuzione

1. Costruisci l'immagine Docker dalla radice del progetto:
   ```
   docker compose build
   ```

2. Avvia il container:
   ```
   docker compose up -d
   ```

(oppure, in un unico comando: ```docker compose up --build -d```).

Il Dockerfile si occuperà di applicare le migrazioni, creare le traduzioni e un superutente locale (se non c'è già).

3. Accedi all'applicazione all'indirizzo http://localhost:8000/

Viene fornita una base dati SQLite3 con dei dati di prova. Il super utente è: `admin:admin`.

## Dispiegamento (_deployment_)
Il progetto è stato pensato per il dispiegamento su siti come Vercel, Heroku, ecc., utilizzando un database PostgreSQL ospitato esternamente (ad esempio su [Supabase](https://supabase.com/), che offre un piano gratuito).

### Prerequisiti
- Un account su [Vercel](https://vercel.com/signup).
- [Vercel CLI](https://vercel.com/docs/cli) installata sulla tua macchina (`npm install -g vercel`).
- Un database PostgreSQL remoto.

### Configurazione della base dati
1. Modificare il `.env` e inserire le credenziali della propria base dati Postgres remota (es. caricata su Supabase). In alternativa:

Imposta la variabile d'ambiente della base dati:
    Vercel ha bisogno di sapere come connettersi al tuo database PostgreSQL. Imposta il `DATABASE_URL` come "secret" di Vercel. Questo evita di esporre le credenziali nel codice.
    Il formato dell'URL è: `postgres://USER:PASSWORD@HOST:PORT/NAME`
    
    vercel secret add DATABASE_URL "postgres://tuo_utente:tua_password@tuo_host:5432/tuo_db"

Il progetto è configurato per utilizzare la libreria `dj_database_url`, che semplifica la configurazione del database tramite una singola variabile d'ambiente.

2. Nel file `ProgettoEventi/settings.py`, assicurati che la sezione `DATABASES` sia configurata in questo modo (le altre configurazioni del database possono essere rimosse o commentate per evitare confusione):


3. Esegui il login al tuo account Vercel (una tantum): `vercel login`
4. Esegui il deploy in produzione: `vercel --prod` (oppure semplicemente quell non in produzione con `vercel deploy`)

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

### Fermare il _container_

Per fermare il _container_ in esecuzione:
```
docker-compose down
```

## Struttura del progetto

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
  - altre filze di configurazione

### Caratteristiche aggiuntive
- Nel file `GestoreEventi/views.py`, la vista `EventListView` utilizza la classe generica `ListView` di Django.
- I modelli hanno diverse relazioni tra di loro nella base dati. Per esempio, in: `models.py` un evento può appartenere a più categorie e una categoria può contenere più eventi. Questa è una relazione _molti-a-molti_ (`ManyToManyField`).
- Il file `GestoreEventi/views.py` mostra l'uso di due permessi diversi per limitare l'accesso a determinate azioni.

## Licenza

Questo progetto è rilasciato sotto licenza libera.