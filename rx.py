#!/usr/bin/env python3

import argparse
import signal
import sys
import time
import logging
import paho.mqtt.client as mqtt

from rpi_rf import RFDevice

rfdevice = None
broker_address = "broker.hivemq.com"
# pylint: disable=unused-argument
def exithandler(signal, frame):
    rfdevice.cleanup()
    sys.exit(0)

def connect_host(c):
    global broker_address
    CONNECTED = False
    while not CONNECTED:
        try:
            c.connect(broker_address) #connect to broker
            CONNECTED = True
            c.publish("/4068f0880b399410602d694b3cc711c8a8f4727e/STATUS","CONNECTED", qos=1, retain=True)#publish
        except:
            print("Connecting to server failed")
            time.sleep(2)
            pass

client = mqtt.Client("P1") #create new instance
client.will_set("/4068f0880b399410602d694b3cc711c8a8f4727e/STATUS","DISCONNECTED",1,retain=True)
connect_host(client)
client.publish("/4068f0880b399410602d694b3cc711c8a8f4727e/STATUS","CONNECTED", qos=1, retain=True)#publish




logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)-15s - [%(levelname)s] %(module)s: %(message)s', )

parser = argparse.ArgumentParser(description='Receives a decimal code via a 433/315MHz GPIO device')
parser.add_argument('-g', dest='gpio', type=int, default=17,
                    help="GPIO pin (Default: 17)")
args = parser.parse_args()

signal.signal(signal.SIGINT, exithandler)
rfdevice = RFDevice(args.gpio)
rfdevice.enable_rx()
timestamp = None
logging.info("Listening for codes on GPIO " + str(args.gpio))
while True:
    if rfdevice.rx_code_timestamp != timestamp:
        # if 1:
        if 250<rfdevice.rx_pulselength<320:
            timestamp = rfdevice.rx_code_timestamp
            logging.info(str(rfdevice.rx_code) +
                     " [pulselength " + str(rfdevice.rx_pulselength) +
                     ", protocol " + str(rfdevice.rx_proto) + "]")
            # print(str(rfdevice.rx_code))
            try:
                client.publish("/4068f0880b399410602d694b3cc711c8a8f4727e/DATA",str(rfdevice.rx_code))
            except:
                client = mqtt.Client("P1") #create new instance
                client.will_set("/4068f0880b399410602d694b3cc711c8a8f4727e/STATUS","DISCONNECTED",1,retain=True)
                connect_host(client)            
                client.publish("/4068f0880b399410602d694b3cc711c8a8f4727e/DATA",str(rfdevice.rx_code))
    time.sleep(0.01)
rfdevice.cleanup()
