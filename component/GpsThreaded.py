import threading
import time
import board
import busio
import adafruit_gps
import math

class ThreadedGPS(threading.Thread):

	# class variables
	# 			gps
	#	float 	latitude
	#	float	longitude
	# 	int		last_fix_time

	def __init__(self, i2c) -> None:
		threading.Thread.__init__(self)

		# initialize the GPS module using the i2c itnerface
		i2c = busio.I2C(board.SCL, board.SDA)
		self.gps = adafruit_gps.GPS_GtopI2C(i2c, debug=False)  # Use I2C interface
		self.gps.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
		self.gps.send_command(b"PMTK220,1000")

		# variable buffer to store values
		self.latitude = 0.0
		self.longitude = 0.0

		# last fix time
		self.last_fix_time = 0

	def get_latitude(self) -> float:
		return self.latitude

	def get_longitude(self) -> float:
		return self.longitude
	
	# this process runs on a separate thread
	def run(self):
		while True:
			has_new_data = self.gps.update()
			if has_new_data:
				print("----- new_data_recieved -----")
				self.latitude = self.gps.latitude
				self.longitude = self.gps.longitude
				self.last_fix_time = time.monotonic()
			time.sleep(0.5)   


if __name__ == "__main__":
	i2c = busio.I2C(board.SCL, board.SDA)
	threaded_gps = ThreadedGPS(i2c)
	threaded_gps.start()

	while True:
		print("Latitude: {0:.6f} degrees".format(threaded_gps.get_latitude()))
		print("Longitude: {0:.6f} degrees".format(threaded_gps.get_longitude()))
		time.sleep(0.75)