# Smart Warehouse - Big Data Platforms

This project implements a real-time, event-driven monitoring system for warehouse logistics, developed as part of the **Industry 4.0 Laboratory** course (Project 2: Big Data Platforms). The system manages stock movements, automated reordering, and security access logs using a modern data stack.

---

## 🏗️ System Architecture

* **Message Broker**: Apache Kafka (KRaft mode)
* **Data Ingestion**: Confluent REST Proxy
* **Database**: PostgreSQL (Relational storage)
* **Logic Layer**: Python-based Consumer (Dockerized) for business logic and validation
* **Data Sink**: Kafka Connect (JDBC Sink) for seamless data persistence
* **Visualization**: Real-time monitoring via Grafana

---

## 🚀 Getting Started

### 🚀 1. Infrastructure Deployment
Launch the entire stack (Kafka, PostgreSQL, Grafana, REST Proxy, Connect, and the Logic Consumer) using Docker Compose:

```bash
docker-compose up -d --build
```

### 💾 2. Database Initialization
Once the containers are running, populate the PostgreSQL database with the required schema and initial dataset by executing the following command:

```bash
cat database/db_population.sql | docker exec -i postgres-db psql -U user -d smart_warehouse
```

### 📊 3. Grafana Monitoring Interface
Access the real-time monitoring dashboard to visualize the warehouse data flow and system logs:

1.  Open your browser and navigate to `http://localhost:3001`.
2.  Log in using the default credentials: **admin / admin**.
3.  Go to **Dashboards** -> **New** -> **Import**.
4.  Upload the `grafana/dashboard_warehouse.json` file and select the **PostgreSQL** data source when prompted.

*Note: The dashboard provides live visualizations for current stock levels, access attempt results, and automated supplier order status.*

### 🔌 4. Kafka Connect Configuration
To activate the automated data flow from Kafka topics to the PostgreSQL database, you must configure the JDBC Sink connectors. Execute the provided automation script located in the root directory:

```bash
# Make the script executable
chmod +x setup_connectors.sh

# Run the configuration script
./setup_connectors.sh
```

### 📱 5. Running the Handheld Terminal Simulator
The handheld terminal simulator is a Python application that mimics real-world warehouse interactions (stock movements and access attempts). It should be executed on your host machine.

#### Prerequisites
* Python 3.x installed on your system.
* A virtual environment is recommended to manage dependencies.

#### Execution Steps
```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# 2. Install required dependencies
pip install requests psycopg2-binary

# 3. Launch the simulator
python src/handheld_terminal_simulator.py
```

---

### 📂 Project Structure
The repository is organized as follows to ensure a clear separation between infrastructure configuration and source code:

```text
.
├── Relazione_smart_warehouse.pdf  # Comprehensive project documentation
├── docker-compose.yaml            # Service orchestration and networking
├── Dockerfile                     # Build instructions for the Logic Consumer
├── requirements.txt               # Python package dependencies
├── setup_connectors.sh            # Automation script for Kafka Connect
├── src/                           # Source code for Consumer & Simulator
├── database/                      # SQL scripts for DB schema and data
├── grafana/                       # Grafana dashboard export (JSON)
└── screenshots/                   # Previews of the system in action
```

---

### 🛡️ Business Logic & Access Control
The **Logic Consumer** serves as the core intelligence of the system, processing incoming events and enforcing specific operational rules:

* **Real-time Validation**: Every transaction from the handheld terminals is intercepted and validated against the PostgreSQL database before being processed.
* **Granular Permissions**:
    * **Admin (ID 1)**: Full authorization across all warehouse sectors.
    * **Operator (ID 2)**: Restricted access; strictly authorized for **Sectors 2 and 3** (Loading/Unloading zones) only. 
* **Security Logging**: Any unauthorized access attempt is blocked by the consumer and immediately logged in the `accesslogs` table for auditing.
* **Automated Reordering**: The system continuously monitors stock levels. If a product's quantity falls below a safety threshold, an automated supplier order is triggered and sent to the `orders` topic.

---

### 👤 Author & Academic Context
This project was developed for academic purposes as part of the **Industry 4.0 Laboratory** course.

* **Author**: Elia Felletti
* **Student ID**: 174557
* **University**: University of Ferrara (UniFe)
* **Course**: Laboratorio di Industria 4.0 - Project 2 (Big Data Platforms)

---

### 📄 License
This project is for educational use only. All rights to the source code and documentation belong to the author.
