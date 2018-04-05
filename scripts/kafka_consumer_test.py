from kafka import KafkaConsumer
import time
import random

while True:
    consumer = KafkaConsumer("equipment", "keyperson", bootstrap_servers="127.0.0.1:9092", group_id="3cf")
    msg = next(consumer)
    consumer.commit()
    consumer.close()
    print("topic: {}; value: {}".format(msg.topic, msg.value))

    time.sleep(5)