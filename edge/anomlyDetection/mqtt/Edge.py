import paho.mqtt.client as mqtt
import time
import numpy as np
class Edge:
    def __init__(self, broker_ip, broker_port):
        self.broker_ip = broker_ip
        self.broker_port = broker_port
        self.client = None
        self.buffer = []

    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("data")

    def on_message(self,client, userdata, msg):
        if msg.topic == 'data':
            data = int(msg.payload)
            self.buffer.append(data)

    def connect(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_ip,self.broker_port, 60)
        self.client.loop_start()

    def publish(self,data,topic):
        self.client.publish(topic,data,2)

    def save(self,filename,scale):
        data = np.asarray(self.buffer,dtype = np.float32)
        data = data[...,np.newaxis]
        data = data/scale
        np.save(filename,data)