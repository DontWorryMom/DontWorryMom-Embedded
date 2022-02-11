import threading
import time
import RPi.GPIO as GPIO

class ThreadedGPIO(threading.Thread):

	# class variables
	# 	int		pin_led
	#	int		pin_button
	#	lambda	button_pressed_handler		// () -> void
	#	lambda	button_released_handler		// () -> void
	#	lambda	blink_finish_handler		// (bool stopped_by_interrupt) -> void
	# 	int		blink_start_time			// time in seconds when blinking started
	#	int 	blink_count
	#	float 	blink_time_on				// in seconds
	#	float	blink_time_off				// in seconds


	# This GPIO module reads from a button and controls an LED
	# if the button is pressed, the button_pressed_handler is called
	# if the button is released, the button_released_handler is called
	# if start_blinking is called, the LED will start blinking
	# if stop_blinking is called, the LED will stop blinking
	# when the LED stops blinking, the function blink_finish_handler will be called
	#	if the LED stopped because stop_blinking is called, then the 
	#	blink_finish_handler will be called with a true value
	#	if the LED stopped because it finished cycling, then the
	#	blink_finish_handler will be called with a false value


	def __init__(self, pin_led, pin_button) -> None:
		threading.Thread.__init__(self)

		self.pin_led = pin_led
		self.pin_button = pin_button
		self.button_pressed_handler = lambda: None
		self.button_released_handler = lambda: None
		self.blink_finish_handler = lambda: None
		self.blink_start_time = time.monotonic()
		self.blink_count = 0
		self.blink_time_on = 1.0
		self.blink_time_off = 1.0

		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pin_button, GPIO.IN, pull_up_down = GPIO.PUD_UP)
		GPIO.setup(self.pin_led, GPIO.OUT)
		GPIO.output(self.pin_led, False)

	def set_pressed_handler(self, handler):
		self.button_pressed_handler = handler
	
	def set_released_handler(self, handler):
		self.button_released_handler = handler
	
	def set_blink_finish_handler(self, handler):
		self.blink_finish_handler = handler
	
	# time_on and time_off are in seconds
	def start_blinking(self, num_times, time_on, time_off):
		self.blink_start_time = time.monotonic()
		self.blink_count = num_times
		self.blink_time_on = time_on
		self.blink_time_off = time_off
	
	def stop_blinking(self):
		current_time = time.monotonic()
		blink_end_time = self.blink_start_time + self.blink_count * (self.blink_time_on + self.blink_time_off) - self.blink_time_off

		self.blink_start_time = 0
		self.blink_count = 0
		self.blink_time_on = 1.0	# this doesn't matter based on impl details
		self.blink_time_off = 1.0	# this doesn't matter either

		if current_time < blink_end_time:
			# blinking was interrupted, so call the finish handler with True
			self.blink_finish_handler(True)	
	
	def button_is_pressed(self) -> bool:
		return not GPIO.input(self.pin_button)

	def set_led(self, on: bool):
		GPIO.output(self.pin_led, on)
	
	# this process runs on a separate thread
	def run(self):
		prev_is_pressed = False
		prev_time = time.monotonic()
		while True:
			# Logic for checking the button and comparing it to the prev value
			is_pressed = self.button_is_pressed()
			if is_pressed != prev_is_pressed:
				if is_pressed:
					self.button_pressed_handler()
				else:
					self.button_released_handler()

			# Logic for setting the LED state on/off
			current_time = time.monotonic()
			blink_end_time = self.blink_start_time + self.blink_count * (self.blink_time_on + self.blink_time_off) - self.blink_time_off
			if current_time > blink_end_time:
				# since we are not in the blinking state, turn the LED off
				self.set_led(on=False)
				# if it was in the blinking state previously, then call the blink stop handler
				if prev_time <= blink_end_time:
					self.blink_finish_handler(False)
			else:
				# we know it is in the blinking state
				# so if it is in the blink on portion, set it on, else set it off
				time_since_start = current_time - self.blink_start_time
				time_since_start %= (self.blink_time_on + self.blink_time_off)
				self.set_led(on=(time_since_start < self.blink_time_on))

			# clean up loop
			prev_is_pressed = is_pressed
			prev_time = current_time


if __name__ == "__main__":
	PIN_LED = 4
	PIN_BUTTON = 14
	threaded_gpio = ThreadedGPIO(PIN_LED, PIN_BUTTON)
	threaded_gpio.set_pressed_handler(
		lambda:	threaded_gpio.start_blinking(5, 1, 0.5)
	)
	threaded_gpio.set_released_handler(
		lambda:	threaded_gpio.stop_blinking()
	)
	threaded_gpio.set_blink_finish_handler(
		lambda x: print(f"finished blinking, stopped_by_interrupted={x}")
	)
	threaded_gpio.start()

	while True:
		continue