import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

ledPin = 4
buttonPin = 14

GPIO.setup(ledPin, GPIO.OUT)
GPIO.setup(buttonPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# button true means it is not pushed
# button false means it is pushed
print("on")
GPIO.output(ledPin, False)


while True:
  buttonState = GPIO.input(buttonPin)
  if buttonState == False:
    print("button pushed")
    GPIO.output(ledPin, True)
  else:
    GPIO.output(ledPin, False)