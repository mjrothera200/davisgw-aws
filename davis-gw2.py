# Davis GW - Adapted from AWS IoT Core Basic Pub Sub

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import serial
import datetime
import threading
import sys
import os


# Setup serial communication to the Feather
ser = serial.Serial(
        port='/dev/ttyACM0',
        baudrate = 19200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)

sensorvalues = { }
rc = 0
# Restart every 12 hours (15 minute send intervals)
ri = 12*4


AllowedActions = ['both', 'publish', 'subscribe']

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")


# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="davisgw",
                    help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="$aws/things/mjrgw1/shadow/update", help="Targeted topic")
parser.add_argument("-m", "--mode", action="store", dest="mode", default="both",
                    help="Operation modes: %s"%str(AllowedActions))
parser.add_argument("-M", "--message", action="store", dest="message", default="Hello World!",
                    help="Message to publish")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
useWebsocket = args.useWebsocket
clientId = args.clientId
topic = args.topic

if args.mode not in AllowedActions:
    parser.error("Unknown --mode option %s. Must be one of %s" % (args.mode, str(AllowedActions)))
    exit(2)

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Port defaults
if args.useWebsocket and not args.port:  # When no port override for WebSocket, default to 443
    port = 443
if not args.useWebsocket and not args.port:  # When no port override for non-WebSocket, default to 8883
    port = 8883


# Configure logging

seriallogger = logging.getLogger('davisgw')
seriallogger.setLevel(logging.INFO)
seriallogHandler = handlers.TimedRotatingFileHandler('/home/pi/logs/serial.log', when='h', backupCount=2,interval=1)
seriallogHandler.setLevel(logging.INFO)
seriallogger.addHandler(seriallogHandler)

logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
logHandler = handlers.TimedRotatingFileHandler('/home/pi/logs/iot.log', when='h', backupCount=24,interval=1)
logger.addHandler(logHandler)

# extract the serial number
cpuserial = "0000000000000000"
try:
    f=open('/proc/cpuinfo', 'r')
    for line in f:
        if line[0:6]=='Serial':
            cpuserial = line[10:26]
    f.close()
except:
    cpuserial="ERROR000000000"

print("CPU Serial # is %s" % (cpuserial))
logger.info("CPU Serial # is %s" % (cpuserial))


# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()

time.sleep(2)

message = { 'state': { 'reported': {} } }
def sendSensorValues():
    logger.info(datetime.datetime.now())
    for fieldname in sensorvalues:
        logger.info(fieldname+' ('+sensorvalues[fieldname]+')')
	message['state']['reported'][fieldname] = sensorvalues[fieldname]
    messageJson = json.dumps(message)
    logger.info('Publishing topic %s: %s\n' % (topic, messageJson))
    myAWSIoTMQTTClient.publish(topic, messageJson, 1)
    threading.Timer(1*60*15, sendSensorValues).start()

threading.Timer(1*60*15,sendSensorValues).start()

# Publish to the same topic in a loop forever
while 1:
        x=ser.readline()
        seriallogger.info(x)
        if (x.startswith('raw')):
                fields = x.split(',')
                # Using for loop
                for i in fields:
                        field = i.split(':')
                        fieldname = field[0].strip()
                        fieldvalue = field[1].strip()
                        # print(fieldname+' ('+fieldvalue+')')
                        sensorvalues[fieldname] = fieldvalue
