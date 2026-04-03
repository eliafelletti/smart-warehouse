1. Setup infrastruttura
docker-compose up -d --build

2. Inizializzazione database
cat database/db_population.sql | docker exec -i postgres-db psql -U user -d smart_warehouse

3. Configurazione Grafana
accedere a localhost:3001 (login admin:admin)
importare la dashboard presente in grafana/dashboard_warehouse.json

4. Configurazione Kafka Connect
Eseguire i 3 curl presenti nel file "setup_connectors.sh"

5. Avvio simulatore palmare
python3 -m venv venv
source venv/bin/activate
pip install requests psycopg2-binary
python3 src/handheld_terminal_simulator.py


Struttura directory
.
├── Relazione_smart_warehouse.pdf          # Documentazione integrale
├── docker-compose.yaml                    # Orchestrazione servizi
├── Dockerfile                             # Build immagine Consumer
├── requirements.txt                       # Dipendenze Python
├── setup_connectors.sh                    # Setup connettori Kafka -> PostgreSQL
├── src/                                   # Codice sorgente (Logic & Simulator)
├── database/                              # Dump SQL (db_population.sql)
├── grafana/                               # Export Dashboard (JSON)
└── screenshots/                           # Allegati visivi (1-4)

Nota sul controllo accessi
Admin (ID 1): accesso completo a tutti i settori
Operatore (ID 2): accesso ai soli settori 2 e 3 (carico/scarico)
