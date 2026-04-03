'''
    Questo file simula il palmare che hanno in dotazione gli operatori di magazzino.
    Previo verifica dell'autorizzazione, l'operatore può:
        1) effettuare un riordino merce manuale;
        2) registrare prelievi o depositi di prodotti in vari settori del magazzino.
'''

import sys
import uuid
import json
import requests
import psycopg2

''' --- VARIABILI GLOBALI --- '''   
# lista prodotti
products = (
    "1  - lamiera",
    "2  - mattone",
    "3  - sabbia (sacco 25kg)",
    "4  - barre di ferro (12mm)",
    "5  - tubi PVC (DN100)",
    "6  - rubinetti (modello A)",
    "7  - cemento (sacco 25kg)",
    "8  - ghiaia (sacco25kg)",
    "9  - piastrelle (mq)",
    "10 - pannelli isolanti (mq)"
)

# lista settori
sectors = (
    "1 - Scaffale A-1",
    "2 - Area Carico",
    "3 - Area Prelievo",
    "4 - Zona Materiali Sfusi",
    "5 - Scaffale B-1"
)

# funzione per la gestione dei messaggi di log riguardanti gli accessi ai settori
def send_access_log(user_id, sector_id, access_granted):
    print(f"Invio log di accesso: user={user_id}, sector={sector_id}, granted={access_granted}")

    rest_proxy_url = "http://localhost:8082/topics/access_events"
    headers = {
        "Content-Type": "application/vnd.kafka.json.v2+json",
    }

    # definisco lo schema per il log di accesso
    schema_definition = {
        "type": "struct",
        "fields": [
            {"type": "string", "optional": False, "field": "log_id"},
            {"type": "int32", "optional": False, "field": "user_id"},
            {"type": "int32", "optional": True, "field": "sector_id"}, 
            {"type": "boolean", "optional": False, "field": "access_granted"}
        ],
        "optional": False,
        "name": "accesslogs.v1"
    }

    data_payload = {
        "log_id": str(uuid.uuid4()),
        "user_id": int(user_id),
        "sector_id": sector_id,
        "access_granted": access_granted
    }

    wrapped_value = {
        "schema": schema_definition,
        "payload": data_payload
    }

    payload = { "records": [{"value": wrapped_value}] }

    # invio il log di accesso "best-effort"
    # non blocco l'utente se questo invio fallisce,
    # ma registriamo l'errore.
    # questo perchè questa operazione è considerabile "secondaria"
    try:
        # uso un timeout breve per non bloccare l'utente
        response = requests.post(
            rest_proxy_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=4 # timeout di 4 secondi
        )
        if response.status_code == 200:
            print("Log di accesso inviato con successo.")
        else:
            print(f"Impossibile inviare il log di accesso. Status: {response.status_code}")
    except Exception as e:
        print(f"Errore durante l'invio del log di accesso: {e}")    


# funzione per la gestione del riordino prodotti
def process_restock(id_user):
    summary = [] # riepilogo operazione da stampare alla fine, prima della conferma

    for product in products:
        print(product)

    # input id prodotto da riordinare, con controllo che sia effettivamente un numero e che rientri nel range accettabile
    print("Inserisci l'id del prodotto da riordinare: ")
    while True:
        try:
            id_product = int(input())
            if id_product in range(1, 11):
                break  # il numero è valido E nel range, esco
            else:
                print(f"ERROR: l'id {id_product} non è nel range 1-10.")
        except ValueError:
            print("ERROR: inserisci un numero valido.")

    summary.append(products[id_product-1])

    # input della quantità di merce da riorinare, con controllo che sia un numero e che sia positivo (non si accettano riordini con quantità negativa o pari a 0)
    print("\nInserisci la quantità di merce da riordinare: ")
    while True:
        try:
            quantity_to_restock = int(input())
            if quantity_to_restock > 0:
                break
            else:
                print("Inserisci una quantità positiva.")
        except ValueError:
            print("ERROR: inserisci un numero valido.")

    summary.append(quantity_to_restock)

    # definizione endpoint del REST Proxy sul topic "orders"
    rest_proxy_url = "http://localhost:8082/topics/orders"

    headers = {
        # specifico, in modo puntiglioso, il content type richiesto dal proxy kafka
        # un contenty type application/json è troppo generico -> error code 415
        "Content-Type": "application/vnd.kafka.json.v2+json",
    }

    # dato che il componente connect richiede un JSON "complesso" dotato di schema, formallizzo il messaggio che il producer invia
    # corrispondenza tra campi e tipi di dati.
    schema_definition = {
        "type": "struct",
        "fields": [
            {"type": "string", "optional": False, "field": "order_id"},
            {"type": "int32", "optional": False, "field": "product_id"},
            {"type": "int32", "optional": False, "field": "user_id"},
            {"type": "int32", "optional": False, "field": "quantity"}
        ],
        "optional": False,
        "name": "supplierorders.v1" # Un nome per lo schema
    }

    data_payload = {
        "order_id": str(uuid.uuid4()), # random ID univoco 
        "product_id" : id_product,
        "user_id" : int(id_user),
        "quantity" : quantity_to_restock,
    }

    # "avvolgo" schema e payload nel formato che JsonConverter si aspetta
    wrapped_value = {
        "schema": schema_definition,
        "payload": data_payload
    }

    # payload finale per il REST Proxy
    payload = {
        "records": [
            {
                "value": wrapped_value
            }
        ]
    }

    return payload, rest_proxy_url, headers, summary


# funzione per la gestione della movimentazione prodotti
def process_stock_movement(user_id, conn):
    summary = [] # riepilogo operazione da stampare alla fine, prima della conferma
    
    # 1. scelta Deposito o Prelievo
    print("\nScegli tipo di movimentazione:")
    print("1 - Deposito (Aggiungi merce)")
    print("2 - Prelievo (Rimuovi merce)")
    choice = input("Scegli (1 o 2): ").strip()

    if choice == '1':
        # --- LOGICA DEPOSITO ---
        op_type = "Deposito"
        print("\n--- Nuovo Deposito ---")

        # input settore di destinazione, con controllo che sia un numero E che rientri nel range accettabile
        for sector in sectors: 
            print(sector)
        print("Inserisci l'id del settore di destinazione: ")
        while True:
            try:
                id_sector = int(input())
                if id_sector in range(1, 6): 
                    break # il numero è valido E nel range, esco
                else: print(f"ERROR: l'id {id_sector} non è nel range 1-5.")
            except ValueError: print("ERROR: inserisci un numero valido.")

        # --- CONTROLLO PERMESSI SETTORE (DEPOSITO) ---
        cursor = conn.cursor()
        # select 1 va a verificare solo l'esistenza di una riga che confermi i permessi, senza dover estrarre dati inutili
        sql_permission_check = """
            SELECT 1 FROM UserSectorPermissions
            WHERE user_id = %s AND sector_id = %s;
        """
        cursor.execute(sql_permission_check, (user_id, id_sector))
        permission = cursor.fetchone()

        # se permission è None, nella tabella UserSectorPermissions non esiste una riga che confermi che questo utente ha i permessi per accedere a questo settore, dunque blocco l'operazione
        if permission is None:
            print(f"\nERRORE: Accesso NEGATO al settore '{sectors[id_sector-1]}'.")

            # registro tentativo di accesso negato
            send_access_log(user_id, id_sector, False)
            return (None, None, None, None, None) # Fallimento
        
        # se arrivo qui, nella tabella UserSectorPermissions esiste una riga che conferma che questo utente ha i permessi per accedere a questo settore
        print(f"Accesso consentito al settore '{sectors[id_sector-1]}'.")
        summary.append(sectors[id_sector-1])

        # input prodotto da depositare, con controllo che sia un numero E che rientri nel range accettabile
        for product in products: 
            print(product)
        print("Inserisci l'id del prodotto da depositare: ")
        while True:
            try:
                id_product = int(input())
                if id_product in range(1, 11): break
                else: print(f"ERROR: l'id {id_product} non è nel range 1-10.")
            except ValueError: print("ERROR: inserisci un numero valido.")
        summary.append(products[id_product-1])

        # input quantità da depositare, con controllo che sia un numero E che sia positivo (non si accettano depositi con quantità negativa o pari a 0)
        print("Inserisci la quantità da depositare: ")
        while True:
            try:
                quantity_to_move = int(input())
                if quantity_to_move > 0: break
                else: print("Inserisci una quantità positiva.")
            except ValueError: print("ERROR: inserisci un numero valido.")
        summary.append(f"+{quantity_to_move}")

    elif choice == '2':
        # --- LOGICA PRELIEVO (con validazione stock) ---
        op_type = "Prelievo"
        print("\n--- Nuovo Prelievo ---")

        # input settore di prelievo, con controllo che sia un numero E che rientri nel range accettabile
        for sector in sectors: 
            print(sector)
        print("Inserisci l'id del settore di prelievo: ")
        while True:
            try:
                id_sector = int(input())
                if id_sector in range(1, 6): 
                    break # il numero è valido E nel range, esco
                else: print(f"ERROR: l'id {id_sector} non è nel range 1-5.")
            except ValueError: print("ERROR: inserisci un numero valido.")

        # --- CONTROLLO PERMESSI SETTORE (PRELIEVO) ---
        cursor = conn.cursor()
        # select 1 va a verificare solo l'esistenza di una riga che confermi i permessi, senza dover estrarre dati inutili
        sql_permission_check = """
            SELECT 1 FROM UserSectorPermissions
            WHERE user_id = %s AND sector_id = %s;
        """
        cursor.execute(sql_permission_check, (user_id, id_sector))
        permission = cursor.fetchone()

        # se permission è None, nella tabella UserSectorPermissions non esiste una riga che confermi che questo utente ha i permessi per accedere a questo settore, dunque blocco l'operazione
        if permission is None:
            print(f"\nERRORE: Accesso NEGATO al settore '{sectors[id_sector-1]}'.")

            # registro tentativo di accesso negato
            send_access_log(user_id, id_sector, False)
            return (None, None, None, None, None) # Fallimento
        
        print(f"Accesso consentito al settore '{sectors[id_sector-1]}'.")
        summary.append(sectors[id_sector-1])

        # Query: estrazione dei soli prodotti CON GIACENZA > 0 in quel settore, per mostrare solo quelli effettivamente prelevabili e validare la scelta dell'utente
        cursor = conn.cursor()
        sql_query = """
            SELECT p.product_id, p.name, i.quantity
            FROM Inventory i
            JOIN Products p ON i.product_id = p.product_id
            WHERE i.sector_id = %s AND i.quantity > 0;
        """
        cursor.execute(sql_query, (id_sector,))
        available_products = cursor.fetchall()

        if not available_products:
            print(f"\nERRORE: Nessun prodotto disponibile trovato nel settore '{sectors[id_sector-1]}'.")
            return (None, None, None, None, None) # Fallimento

        # stampa la lista dei prodotti disponibili e crea una mappa per la validazione
        print("\nProdotti disponibili in questo settore:")
        stock_map = {} # dizionario per validare: {product_id: quantity}
        for row in available_products:
            # row[0]=id, row[1]=name, row[2]=qty
            print(f"  ID: {row[0]} - {row[1]} (Disponibili: {row[2]})")
            stock_map[row[0]] = row[2]

        # input id prodotto da prelevare, con controllo che sia un numero E che corrisponda a un prodotto con stock > 0 in quel settore (validazione tramite la mappa)
        print("\nInserisci l'id del prodotto da prelevare: ")
        while True:
            try:
                id_product = int(input())
                if id_product in stock_map: 
                    break # il numero è valido E corrisponde a un prodotto con stock > 0, esco
                else: print(f"ERROR: Inserisci un ID valido tra quelli elencati.")
            except ValueError: print("ERROR: inserisci un numero valido.")
        
        product_name = [p[1] for p in available_products if p[0] == id_product][0]
        summary.append(f"{product_name}")

        # input quantità da prelevare, con controllo che sia un numero E che sia positivo E che non superi la quantità disponibile (validazione tramite la mappa)
        max_qty = stock_map[id_product]
        print(f"Quanti '{product_name}' vuoi prelevare? (Max: {max_qty}): ")
        while True:
            try:
                quantity = int(input())
                if 0 < quantity <= max_qty: 
                    break
                else: 
                    print(f"ERROR: Inserisci un numero tra 1 e {max_qty}.")
            except ValueError: print("ERROR: inserisci un numero valido.")
        
        quantity_to_move = -quantity # il movimento deve essere negativo per indicare un prelievo
        summary.append(quantity_to_move)

    else:
        print("Scelta non valida.")
        return (None, None, None, None, None) # Fallimento
    
    # --- COSTRUZIONE PAYLOAD KAFKA (Comune a entrambi) ---
    
    rest_proxy_url = "http://localhost:8082/topics/stock_movements"
    headers = {
        "Content-Type": "application/vnd.kafka.json.v2+json",
    }

    schema_definition = {
        "type": "struct",
        "fields": [
            {"type": "string", "optional": False, "field": "log_id"},
            {"type": "int32", "optional": False, "field": "product_id"},
            {"type": "int32", "optional": False, "field": "sector_id"},
            {"type": "int32", "optional": False, "field": "user_id"},
            {"type": "int32", "optional": False, "field": "quantity"}
        ],
        "optional": False,
        "name": "stockmovement.v1"
    }

    data_payload = {
        "log_id": str(uuid.uuid4()),
        "product_id": id_product,
        "sector_id": id_sector,
        "user_id": int(user_id),
        "quantity": quantity_to_move
    }

    wrapped_value = {
        "schema": schema_definition,
        "payload": data_payload
    }

    payload = { "records": [{"value": wrapped_value}] }
    
    # aggiungo il tipo di operazione in testa al summary perchè regolerà il tipo di stampa, poco prima del check finale di conferma operazione
    summary.insert(0, op_type)

    return payload, rest_proxy_url, headers, summary, id_sector


def main():
    ''' STEP 0: CONFIGURAZIONE CONNESSIONE CON DB '''
    conn_config = {
        "host": "localhost",
        "port": 5432,
        "database": "smart_warehouse",
        "user": "user",
        "password": "password"
    }
    
    # inzialmente inizializzata a None per poi richiamarla successivamente
    conn = None

    try:
        conn = psycopg2.connect(**conn_config)
        cursor = conn.cursor()
        print("Configurazione completata con successo!\n")
        
        ''' --- STEP 1: INPUT ID OPERATORE --- '''
        operator_id_str = input("Inserisci il tuo ID operatore: ").strip()
        try:
            operator_id = int(operator_id_str) # conversione in int
        except ValueError:
            print(f"ERRORE: L'ID operatore '{operator_id_str}' non è un numero.")
            conn.close()
            sys.exit(9)

        # controllo che l'ID operatore non sia 0, in quanto è riservato al sistema di riordino automatico e non deve essere usato per operazioni manuali
        if operator_id == 0:
            print("accesso negato: l'ID 0 è riservato al sistema di riordino automatico e non può essere usato per operazioni manuali.")
            conn.close()
            sys.exit(10)

        ''' --- STEP 1.1: VERIFICA ESISTENZA OPERATORE E RUOLO --- '''
        sql_check = """
            SELECT role, username
            FROM users
            WHERE user_id = %s;
        """
        cursor.execute(sql_check, (operator_id,))
        result = cursor.fetchone()

        if result is None:
            print(f"Nessuna informazione per l'ID utente: {operator_id}; controlla che l'ID sia corretto.\n")
            conn.close()
            sys.exit(2)
        else:
            role = result[0]
            name = result[1]

        ''' --- STEP 2: OPERAZIONI SU PRODOTTO (prelievo o riordino manuale) --- '''

        # definisco le variabili prima, per sicurezza
        payload, rest_proxy_url, headers, summary = None, None, None, None 
        id_sector = None      

        if role == "admin":
            print(f"Admin {name} con id: {operator_id} abilitato al riordino manuale e alla movimentazione prodotti.\n")

            print("Scegli l'operazione che si desidera effettuare: ")
            print("1 - riordino prodotti")
            print("2 - movimentazione prodotti\n")
            operation = input("\nInserisci numero operazione (1 o 2): ")
            if operation == "1":
                payload, rest_proxy_url, headers, summary = process_restock(operator_id)
            elif operation == "2":
                payload, rest_proxy_url, headers, summary, id_sector = process_stock_movement(operator_id, conn)
            else:
                print("Operazione non valida.")

        elif role == "operatore":
            print(f"Operatore {name} con id: {operator_id} abilitato alla movimentazione prodotti.\n")
            payload, rest_proxy_url, headers, summary, id_sector = process_stock_movement(operator_id, conn)
        else:
            print(f"Utente con id: {operator_id} non abilitato ad effettuare operazioni.\n")
            # registro comunque che un operatore, con un ID che sono sicuro esista, non addetto a nessuna operazione di magazzino ha tentato di accedere
            send_access_log(operator_id, None, False)
            conn.close()
            sys.exit(3)
        
        # a questo punto sono sicuro che l'utente esiste, è autorizzato e procedo con l'invio dell'operazione
        ''' --- STEP 3: INVIO RICHIESTA --- '''
        # errore durante la fase di raccolta dati per costruzione payload -> annullo operazione
        if payload is None:
            print("\nOperazione annullata o non valida. Nessun dato inviato.")
            conn.close()
            sys.exit(4)

        else:
            # in base al tipo di operazione, stampo un riepilogo diverso
            if summary[0] == "Prelievo" or summary[0] == "Deposito":
                print(f"\n\nRiepilogo {summary[0]}:")
                print(f"Settore: {summary[1]}")
                print(f"Prodotto: {summary[2]}")
                print(f"Quantità: {summary[3]}")
                print(f"Utente: {name}")
            else: 
                print("\n\nRiepilogo ordine: ")
                print(f"Prodotto: {summary[0]}")
                print(f"Quantità: {summary[1]}")
                print(f"Utente: {name}")

        print("\n\nConfermare operazione (si/no)")
        check = input().lower()
        if check == "si":
            # chiamata POST al REST Proxy per inviare il messaggio al topic Kafka
            try:
                response = requests.post(
                    rest_proxy_url,
                    data=json.dumps(payload), # conversione payload in formato JSON
                    headers=headers
                )

                # controllo esito della chiamata
                if response.status_code == 200:
                    print("Messaggio inviato con succcesso al server.")

                    # se id_sector is None                     -> sto processando un restock, quindi non devo registrare tentativi di accesso fisico al magazzino
                    # se id_sector is not None (è valorizzato) -> sto processando uno stock movement che comporta accesso fisico al magazzino, dunque registro
                    if id_sector is not None:
                        # invio log di accesso positivo
                        print("Invio log di accesso confermato...")
                        send_access_log(operator_id, id_sector, True)
                else:
                    print("\nErrore durante l'invio del messaggio.")
                    print(f"Status Code: {response.status_code}")
                    print(f"Risposta: {response.text}")

            except requests.exceptions.ConnectionError as e:
                print(f"\nErrore di connessione: Impossibile raggiungere il REST Proxy.")
                print(f"Dettagli errore: {e}")
                sys.exit(1)
        else:
            print("Operazione annullata.")
    except KeyboardInterrupt:
        print("\nTerminazione...")
    except Exception as e:
        print(f"Errore generico: {e}")
    finally:
        conn.close()

    

if __name__ == "__main__":
    main()