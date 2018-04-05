from kafka import KafkaProducer
import random

producer = KafkaProducer(bootstrap_servers="127.0.0.1:9092")

for i in range(10):
    producer.send(topic="keyperson", value="TEST{}".format(i).encode())

producer.close()