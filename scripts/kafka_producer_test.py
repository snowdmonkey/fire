from kafka import KafkaProducer
import random

producer = KafkaProducer(bootstrap_servers="159.99.234.162:9092")

for i in range(10):
    producer.send(topic="face", value="TEST{}".format(i).encode())

producer.close()