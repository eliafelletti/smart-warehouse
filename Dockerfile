# 1. immagine Python ufficiale e leggera
FROM python:3.10-slim

# 2. set cartella di lavoro all'interno del container
WORKDIR /app

# 3. copia file dei requisiti
COPY requirements.txt .

# 4. installazione requisiti
RUN pip install --no-cache-dir -r requirements.txt

# 5. copia dello script Python che contiene la logica del consumer
COPY src/logic_consumer.py .

# 6. comando di avvio del consumer
CMD ["python", "logic_consumer.py"]