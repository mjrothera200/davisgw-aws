import logging
import logging.handlers as handlers
import time
import argparse
import json
import RPi.GPIO as GPIO
import dht11
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
# Configure logging

seriallogger = logging.getLogger('monitor-serial')
seriallogger.setLevel(logging.INFO)
seriallogHandler = handlers.TimedRotatingFileHandler('/home/pi/logs/monitor-serial.log', when='h', backupCount=2,interval=1)
seriallogHandler.setLevel(logging.INFO)
seriallogger.addHandler(seriallogHandler)


# Publish to the same topic in a loop forever
while 1:
        x=ser.readline()
        seriallogger.info(x)
	print(x)
        if (x.startswith('raw')):
                fields = x.split(',')
                # Using for loop
                for i in fields:
                        field = i.split(':')
                        fieldname = field[0].strip()
                        fieldvalue = field[1].strip()
                        # print(fieldname+' ('+fieldvalue+')')
                        sensorvalues[fieldname] = fieldvalue

