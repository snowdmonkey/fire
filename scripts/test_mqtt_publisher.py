import paho.mqtt.client as mqtt


client = mqtt.Client(client_id="xuefeng")

client.username_pw_set(username="xuefeng", password="HON123well")
client.connect("159.99.234.162", port=1883)
client.publish(topic="test111", payload="test message 2")
client.disconnect()