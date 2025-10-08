from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],  # Adjust to your Kafka address
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_event():
    return {
        'user_id': random.randint(1, 100),
        'event_type': random.choice(['click', 'view', 'purchase']),
        'timestamp': datetime.now().isoformat(),
        'value': random.randint(1, 100)
    }

if __name__ == '__main__':
    topic = 'user_events'
    print(f"Producing messages to {topic}...")
    
    while True:
        event = generate_event()
        producer.send(topic, event)
        print(f"Sent: {event}")
        time.sleep(1)
