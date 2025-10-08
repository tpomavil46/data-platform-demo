from kafka import KafkaConsumer
import json
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Postgres connection
conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    database=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD')
)
cur_test = conn.cursor()
cur_test.execute("SELECT current_database(), inet_server_addr(), inet_server_port(), version()")
print(f"CONSUMER CONNECTED TO: {cur_test.fetchone()}")
cur_test.close()
cur = conn.cursor()

# Create table if not exists
cur.execute("""
    CREATE TABLE IF NOT EXISTS streaming.user_events (
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
    group_id='python-consumer',
    auto_offset_reset='earliest'
)

print("Consuming messages and writing to Postgres...")

for message in consumer:
    # print(f"DEBUG: Received message from Kafka: {message.value}")
    event = message.value
    user_id = event['user_id']
    event_type = event['event_type']
    
    # print(f"DEBUG: About to insert user_id={user_id}, event_type={event_type}")
    
    # Upsert into Postgres
    cur.execute("""
        INSERT INTO streaming.user_events (user_id, event_type, event_count)
        VALUES (%s, %s, 1)
        ON CONFLICT (user_id, event_type)
        DO UPDATE SET event_count = streaming.user_events.event_count + 1
    """, (user_id, event_type))
    
    # print(f"DEBUG: Executed query")
    conn.commit()
    # print(f"DEBUG: Committed to DB")
    print(f"Processed: user {user_id}, event {event_type}")