from kafka import KafkaConsumer
import json
import psycopg2
from psycopg2.extras import execute_values

# Postgres connection
conn = psycopg2.connect(
    host="localhost",
    database="your_db",
    user="your_user",
    password="your_password"
)
cur = conn.cursor()

# Create table if not exists
cur.execute("""
    CREATE TABLE IF NOT EXISTS user_events (
        user_id INT,
        event_type VARCHAR(50),
        event_count INT,
        created_at TIMESTAMP DEFAULT NOW(),
        PRIMARY KEY (user_id, event_type)
    )
""")
conn.commit()

# Kafka consumer
consumer = KafkaConsumer(
    'user_events',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='python-consumer'
)

print("Consuming messages and writing to Postgres...")

for message in consumer:
    event = message.value
    user_id = event['user_id']
    event_type = event['event_type']
    
    # Upsert into Postgres
    cur.execute("""
        INSERT INTO user_events (user_id, event_type, event_count)
        VALUES (%s, %s, 1)
        ON CONFLICT (user_id, event_type)
        DO UPDATE SET event_count = user_events.event_count + 1
    """, (user_id, event_type))
    
    conn.commit()
    print(f"Processed: user {user_id}, event {event_type}")