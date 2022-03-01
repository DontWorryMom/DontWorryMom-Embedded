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

# Global Vars
crash_lat = None
crash_lon = None
crash_acc = None

#communication with server
url = "https://dwm-spring-prod.herokuapp.com/locations/deviceId/6"
data = {}

def button_pressed():
	print("button was pressed")

def button_released():
	print("button was released")

def blinking_finished(was_interrupted: bool):
  if was_interrupted:
    # since button was pressed, we dont need to send data
    print("button was let go")
  else:
    # button was not pressed
    send_data(crash_acc, crash_lat, crash_lon)
    print("led stopped flashing because of timeout")

def send_data(peak_accel, lat, lon):
  print(f"peak_accel={peak_accel}, lat={lat}, lon={lon}")
  data = {"locationLat": lat, "locationLon": lon, "maxAcceleration": max_acceleration}
  r = requests.post(url, json=data)
  print(r.text)

# Main Loop

if __name__ == "__main__":
  # setup I2C interface
  i2c = busio.I2C(board.SCL, board.SDA)
  
  # setup GPIO stuff
  threaded_gpio = ThreadedGPIO(PIN_LED, PIN_BUTTON)
  threaded_gpio.set_pressed_handler(lambda: threaded_gpio.stop_blinking())
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
    
    # get the current location
    lat = threaded_gps.get_latitude()
    lon = threaded_gps.get_longitude()
        
    # calculate the max acceleration
    accel = accelerometer.acceleration
    max_acceleration = math.sqrt((accel[0] ** 2) + (accel[1] ** 2) + (accel[2] ** 2))
        
    if max_acceleration >= 18:
      # start blinking
      # if button is pressed, then don't send crash
      # if button is not pressed, then send crash
      crash_acc = max_acceleration
      crash_lat = lat
      crash_lon = lon
      threaded_gpio.start_blinking(5, 0.5, 0.5)    # blink for 5 seconds
      time.sleep(5.0)                              # while blinking, pause this thread
    else:
      # if time since last data is > 30, send
      if current_time - last_send_time > 5:
        if (lat != 0 or lat != None) and (lon != 0 or lon != None):
          print(accelerometer.acceleration, max_acceleration, lat, lon)
          
          data = {"locationLat": lat, "locationLon": lon, "maxAcceleration": max_acceleration}
          r = requests.post(url, json=data)
          print(r.text)
          
          last_send_time = current_time  
        
      
    """
    # if it is over the threshold, then we start blinking
    if not threaded_gpio.button_is_pressed() and max_acceleration > 9.9:
      button_pressed()
      threaded_gpio.start_blinking(5, 0.1, 0.1)
		# if the button is pressed while blinking, then we
		#		stop blinking, and send different payload
    elif threaded_gpio.button_is_pressed() and max_acceleration > 9.9:
      button_released()
      threaded_gpio.stop_blinking()
    # if the LED stops blinking without the button being pressed
 		#		then we send the payload
 		# send payload every 30 seconds or something
    #else:
      #print("send payload")
    
    if (current_time - last_send_time) > 0.5:
      print(max_acceleration)
      print(accelerometer.acceleration, threaded_gps.get_latitude(), threaded_gps.get_longitude())
      last_send_time = current_time  
      """
    """
      data = {"locationLat": lat, "locationLon": lon, "maxAcceleration": max_acceleration}
      r = requests.post(url, json=data)
      print(r.text)
    """

