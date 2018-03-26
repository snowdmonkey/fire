import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    # print("message received")
    print(msg.topic+": "+str(msg.payload))

def on_connect(client, userdata, flags, rc):
    print("connected with result code {}".format(rc))
    client.subscribe("#")

client = mqtt.Client(client_id="client-002")

client.username_pw_set(username="xuefeng", password="HON123well")

client.on_message = on_message
client.on_connect = on_connect

client.connect("159.99.234.162", port=1883)
# client.connect("xuefeng:HON123well@159.99.234.162:1883")
# client.subscribe("test", 2)

client.loop_forever()

# import time
# import paho.mqtt.client as paho
# broker="159.99.234.162"
# #define callback
# def on_message(client, userdata, message):
#     time.sleep(1)
#     print("received message =",str(message.payload.decode("utf-8")))
# client= paho.Client("client-001") #create client object client1.on_publish = on_publish #assign function to callback client1.connect(broker,port) #establish connection client1.publish("house/bulb1","on")
# ######Bind function to callback
# client.on_message=on_message
# #####
# print("connecting to broker ",broker)
# client.username_pw_set(username="xuefeng", password="HON123well")
# client.connect(broker)#connect
# client.loop_start() #start loop to process received messages
# print("subscribing ")
# client.subscribe("house/bulb1")#subscribe
# time.sleep(2)
# print("publishing ")
# client.publish("house/bulb1","on")#publish
# time.sleep(4)
# client.disconnect() #disconnect
# client.loop_stop() #stop loop