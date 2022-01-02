import RPi.GPIO as GPIO
import dht11
import time
import datetime

# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

# read data using pin 17
instance = dht11.DHT11(pin=17)

try:
	while True:
		result = instance.read()
		if result.is_valid():
			print("Last valid input: " + str(datetime.datetime.now()))
			print("Temperature: %-3.1f C" % result.temperature)
			fahrenheit = (result.temperature*9)/5 + 32
			print("Temperature: %-3.1f F" % fahrenheit)
			print("Humidity: %-3.1f %%" % result.humidity)
		time.sleep(6)

except KeyboardInterrupt:
    print("Cleanup")
    GPIO.cleanup()
