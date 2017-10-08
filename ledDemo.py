import time
import RPi.GPIO as GPIO ## Import GPIO library
GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
GPIO.setwarnings(False)

print("This program will blink the LED twice on ProdBoard")

GPIO.setup(29, GPIO.OUT)
GPIO.output(29,False)
GPIO.setup(37, GPIO.OUT)
GPIO.output(37,False)


GPIO.setup(29, GPIO.OUT) 
GPIO.output(29,True)
GPIO.setup(37, GPIO.OUT) 
GPIO.output(37,True) 

time.sleep(2)
GPIO.setup(29, GPIO.OUT)
GPIO.output(29,False)
GPIO.setup(37, GPIO.OUT)
GPIO.output(37,False)

time.sleep(2)

GPIO.setup(29, GPIO.OUT)
GPIO.output(29,True)
GPIO.setup(37, GPIO.OUT)
GPIO.output(37,True)

time.sleep(2)
GPIO.setup(29, GPIO.OUT)
GPIO.output(29,False)
GPIO.setup(37, GPIO.OUT)
GPIO.output(37,False)

