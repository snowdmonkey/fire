import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, msg):
    # print("message received")
    print(msg.topic+": "+str(msg.payload))

def on_connect(client, userdata, flags, rc):
    print("connected with result code {}".format(rc))
    client.subscribe("#", 2)

client = mqtt.Client(client_id="3cf")

client.username_pw_set(username="xuefeng", password="HON123well")

client.on_message = on_message
client.on_connect = on_connect

client.connect("159.99.234.162", port=1883)
# client.loop(1)
# client.loop_forever()

while True:
    print("start a loop")
    client.loop()
    time.sleep(1)

#
# while True:
#     client.connect("159.99.234.162", port=1883)
#     client.loop(1)
#     client.disconnect()