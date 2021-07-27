import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, message):
    print("Topic:", message.topic)
    print("Message:", str(message.payload.decode("utf-8")))

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True
        print("Log:", "Connection successful")
    else:
        print("Log:", "Bad connection. Returned code:", rc)

def on_disconnect(client, userdata, rc):
    print("Log:", "Disconnected. Returned code:", rc)
    client.connected_flag = False
    client.disconnect_flag = True

broker_address = "broker.emqx.io"
topic = "laundrobot"
client_id = "sub"

client = mqtt.Client(client_id)
client.on_message = on_message
client.on_connect = on_connect

print("Log:", "Connecting to broker")
client.connected_flag = False
client.connect(broker_address)
while client.connected_flag:
    print("Log:", "waiting")
    time.sleep(1)

# client.loop_forever()
client.loop_start()

topic = "laundrobot"
print("Log:", "Subscribing to topic", topic)
client.subscribe(topic)

while True:
    time.sleep(1)

#client.loop_stop()




