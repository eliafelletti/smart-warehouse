'''
    Questo consumer implementa le logiche di business riguardanti:
        - punto 2: gestione prodotti in stock -> update a seguito di depositi e prelievi
        - punto 3: invio automatica dell'ordine di restock quando al quantità di n certo prodotto scende al di sotto della soglia minima
'''

from confluent_kafka import Consumer, Producer
import json
import uuid
import psycopg2

# funzione che gestirà i prelievi/depositi e i riordini automatici
def process_stock_movement(data, cursor, producer, consumer):
    try:
        # estrazione dati
        product_id = data['product_id']
        sector_id = data['sector_id']
        user_id = data['user_id']
        quantity_to_move = data['quantity']

        print(f"Processo: product={product_id}, quantity={quantity_to_move}, user={user_id}")

        if quantity_to_move > 0:
            # --- LOGICA DEPOSITO (UPSERT) ---
            # inserisco una nuova riga o, se già esiste, la aggiorno aumentando la quantità 
            print("Eseguo UPSERT (Deposito)...")
            sql_upsert = """
                INSERT INTO Inventory (product_id, sector_id, quantity)
                VALUES (%s, %s, %s)
                ON CONFLICT (product_id, sector_id)
                DO UPDATE SET quantity = Inventory.quantity + %s;
            """
            # Nota: quantity_to_move viene passato due volte:
            # 1. per il nuovo INSERT (es. 100)
            # 2. per l'UPDATE (es. 50 + 100)
            cursor.execute(sql_upsert, (product_id, sector_id, quantity_to_move, quantity_to_move))
            print("Eseguito UPSERT su Inventory.")

        elif quantity_to_move < 0:
            # --- LOGICA PRELIEVO (SOLO UPDATE) ---
            # eseguo un semplice UPDATE
            # il vincolo CHECK (quantity >= 0) del DB fornisce ulteriore protezione.
            print("Eseguo UPDATE (Prelievo)...")
            sql_update = """
                UPDATE Inventory 
                SET quantity = quantity + %s 
                WHERE product_id = %s AND sector_id = %s
            """
            cursor.execute(sql_update, (quantity_to_move, product_id, sector_id))
            
            # Se l'UPDATE non ha toccato righe (prodotto/settore non esiste), fallisci
            if cursor.rowcount == 0:
                raise Exception(f"Nessuna riga trovata per product={product_id}, sector={sector_id}. Prelievo non valido.")
            
            print("Eseguito UPDATE su Inventory.")
        
        else:
            # quantity_to_move == 0, non faccio nulla)
            # le movimentazioni con quantità 0 non dovrebbero essere concesse dal simulatore, ma gestisco comunque il caso in modo esplicito
            print("Quantità è 0, nessuna operazione sul DB.")
            # esco, ma lo considero un successo (il blocco 'else' farà il commit)
            pass

        # controllo lo stock totale del prodotto, sommando tutte le quantità di ogni settore
        sql_check = """
                SELECT SUM(i.quantity), p.reorder_threshold, p.name
                FROM Inventory i
                JOIN Products p ON i.product_id = p.product_id
                WHERE i.product_id = %s
                GROUP BY p.reorder_threshold, p.name;
            """
        cursor.execute(sql_check, (product_id,))
        
        result = cursor.fetchone()
        if result is None:
            print(f"[WARN] Nessun dato inventario trovato per product_id {product_id}. Salto controllo soglia.")
            cursor.connection.commit() # committ comunque dell'UPDATE
            return 

        current_stock_total, threshold, product_name = result
        print(f"Stock totale per '{product_name}': {current_stock_total} (Soglia: {threshold})")

        # se lo stock totale è inferiore alla soglia, invio un messaggio di riordine al topic 'orders' ---> riordino automatico
        if current_stock_total < threshold:
            print("Soglia minima raggiunta, avvio riordine automatico")

            schema_definition = {
                "type": "struct",
                "fields": [
                    {"type": "string", "optional": False, "field": "order_id"},
                    {"type": "int32", "optional": False, "field": "product_id"},
                    {"type": "int32", "optional": False, "field": "user_id"},
                    {"type": "int32", "optional": False, "field": "quantity"}
                ],
                "optional": False,
                "name": "supplierorders.v1" 
                }

            data_payload = {
                "order_id": str(uuid.uuid4()), # random ID univoco 
                "product_id" : product_id,
                "user_id" : 0, # user 0 corrisponde all'auto_reorder_system
                "quantity" : 100, # quantità fissa
            }

            # "avvolgo" schema e payload nel formato che JsonConverter si aspetta
            wrapped_value = {
                "schema": schema_definition,
                "payload": data_payload
            }

            # invio riordine automatico al topic 'orders'
            producer.produce('orders', json.dumps(wrapped_value))
            producer.flush() # forza l'invio immediato
            print("Messaggio di riordino per 100 pz inviato al topic 'orders'.")
    except Exception as e:
        print(f"ERRORE GRAVE durante process_stock_movement: {e}")
        print("Eseguo ROLLBACK delle modifiche al DB.")
        cursor.connection.rollback() # annulla la transazione
    else:
        # questo blocco 'else' viene eseguito solo se il 'try' ha successo
        print("Transazione completata con successo. Eseguo COMMIT.")
        cursor.connection.commit() # conferma la transazione (UPDATE e/o RIORDINO)

        # se sono arrivato qui, il messaggio è stato processato (bene o male).
        # dico a Kafka di non inviarlo ulteriormente
        consumer.commit(asynchronous=False)


def main():
    # --- CONSUMER ---
    # specifico la posizione del kafka broker
    consumer_config = {
        "bootstrap.servers" : "kafka:29092",
        "group.id" : "logic-consumer", # mi identfica il gruppo di appartenenza del consumatore
        "auto.offset.reset" : "earliest", # se non si è in grado di risalire all'ultimo messaggio letto si inizia dall'inizio del topic
        "enable.auto.commit": "false" # disabilito l'auto commit dei messaggi per gestirlo manualmente
    }

    # istanziazione consumer
    consumer = Consumer(consumer_config)    
    
    # iscrizione del consumer al topic stock_movements (quello che contiene i messaggi di deposito/prelievo da processare)
    consumer.subscribe(["stock_movements"])

    print(f"Consumer in esecuzione e iscritto al topic stock_movements...")

    # --- PRODUCER ---
    producer_config = {
        "bootstrap.servers" : "kafka:29092",
    }

    # istanziazione producer
    producer = Producer(producer_config)

    # --- DATABASE postgres ---
    # connessione al db postgres
    conn_config = {
        "host": "postgres-db",
        "port": 5432,
        "database": "smart_warehouse",
        "user": "user",
        "password": "password"
    }
    
    # inizializzata a None per poi richiamarla successivamente
    conn = None

    try:
        conn = psycopg2.connect(**conn_config)
        cursor = conn.cursor()
        print("Connesso al DB!\n")

        while True:
            msg = consumer.poll(1.0) # controllo ogni secondo se nel topic sono presenti nuovi messaggi

            if msg is None:
                continue # non è presente nessun nuovo messaggio
            if msg.error():
                print("Error:", msg.error())
                continue

            # estrazione topic di provenienza del messaggio
            topic = msg.topic()

            # estrazione dati del messaggio 
            try:
                data = json.loads(msg.value())
            except json.JSONDecodeError:
                print(f"ERRORE: messaggio non JSON valido; messaggio ignorato")
                continue # ignora il messaggio corrente

            if topic == "stock_movements":
                print("Ricevuto messaggio da stock_movements.")
                # chiama la funzione che processa il messaggio e gestisce sia i movimenti di stock che i riordini automatici
                process_stock_movement(data["payload"], cursor, producer, consumer)
            else:
                print(f"Messaggio ricevuto da topic sconosciuto. ({topic})")
    except KeyboardInterrupt:
        print("\nTerminazione consumer...")
    except Exception as e:
        print(f"ERRORE generico: {e}")
    finally:
        # teoricamente, questo punto non dovrebbe mai essere raggiunto perché il consumer è in un loop infinito, ma è buona pratica chiudere le risorse in un blocco finally
        if consumer:
            consumer.close()
        if producer:
            producer.flush() 
            producer.close() 
        if conn:
            conn.close()


if __name__ == "__main__":
    main()