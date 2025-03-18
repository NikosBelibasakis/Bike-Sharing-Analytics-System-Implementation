#v1
from kafka import KafkaProducer
import json

def create_kafka_producer():
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    return producer

def send_data_to_kafka(producer, topic, data):
    try:
        producer.send(topic, data)
        producer.flush()
        print(f"Data sent to topic {topic}")
    except Exception as e:
        print(f"Error sending data to {topic}: {e}")