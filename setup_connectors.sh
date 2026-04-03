curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d '{
  "name": "jdbc-sink-orders",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
    "connection.url": "jdbc:postgresql://postgres-db:5432/smart_warehouse",
    "connection.user": "user",
    "connection.password": "password",
    "topics": "orders",
    "table.name.format": "supplierorders",
    "insert.mode": "insert",
    "auto.create": "false",
    
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "true",

    "pk.mode": "record_value",
    "pk.fields": "order_id",
    
    "fields.whitelist": "order_id,product_id,user_id,quantity"
  }
}'

curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d '{
  "name": "jdbc-sink-stock-movements",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
    "connection.url": "jdbc:postgresql://postgres-db:5432/smart_warehouse",
    "connection.user": "user",
    "connection.password": "password",
    "topics": "stock_movements",
    "table.name.format": "stockmovementslog",
    "insert.mode": "insert",
    "auto.create": "false",
    
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "true",

    "pk.mode": "record_value",
    "pk.fields": "log_id",
    
    "fields.whitelist": "log_id,product_id,user_id,sector_id,quantity"
  }
}'

curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d '{
  "name": "jdbc-sink-access-events",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
    "connection.url": "jdbc:postgresql://postgres-db:5432/smart_warehouse",
    "connection.user": "user",
    "connection.password": "password",
    "topics": "access_events",
    "table.name.format": "accesslogs",
    "insert.mode": "insert",
    "auto.create": "false",
    
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "true",

    "pk.mode": "record_value",
    "pk.fields": "log_id",
    
    "fields.whitelist": "log_id,user_id,sector_id,access_granted"
  }
}'
