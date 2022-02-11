import time
import math
from component.GpsThreaded import ThreadedGPS
from component.ButtonLedThreaded import ThreadedGPIO
import board
import busio
import adafruit_adxl34x
import requests

# Define Constants
PIN_LED = 4
PIN_BUTTON = 14


def button_pressed():
	print("button was pressed")

def button_released():
	print("button was released")

def blinking_finished(was_interrupted: bool):
	if was_interrupted:
		print("button was let go")
	else:
		print("led stopped flashing because of timeout")

def send_data(peak_accel, lat, lon):
	print(f"peak_accel={peak_accel}, lat={lat}, lon={lon}")


# Main Loop

if __name__ == "__main__":
	# setup I2C interface
	i2c = busio.I2C(board.SCL, board.SDA)

	# setup GPIO stuff
	threaded_gpio = ThreadedGPIO(PIN_LED, PIN_BUTTON)
	threaded_gpio.set_pressed_handler(button_pressed)
	threaded_gpio.set_released_handler(button_released)
	threaded_gpio.set_blink_finish_handler(blinking_finished)

	# setup GPS stuff
	threaded_gps = ThreadedGPS(i2c)

	# setup accelerometer
	accelerometer = adafruit_adxl34x.ADXL345(i2c)

	# start threads
	threaded_gpio.start()
	threaded_gps.start()
	
	# run main loop
	last_send_time = time.monotonic()
	while True:
		current_time = time.monotonic()

		# calculate the max acceleration
		# if it is over the threshold, then we start blinking
		# if the button is pressed while blinking, then we
		#		stop blinking, and send different payload
		# if the LED stops blinking without the button being pressed
		#		then we send the payload
		# send payload every 30 seconds or something

		if (current_time - last_send_time) > 0.5:
			send_data(
				accelerometer.acceleration, 
				threaded_gps.get_latitude(), 
				threaded_gps.get_longitude()
			)
			last_send_time = current_time