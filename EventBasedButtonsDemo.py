'''
Copyright [2017] [Nanomesher Limited - www.nanomesher.com]

Licensed under the Apache License, Version 2.0 (the "License"); you may not use$

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed$
'''


import RPi.GPIO as GPIO  
import time
GPIO.setmode(GPIO.BCM)

GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)



def button1_callback(channel):
  print("Button 1 callback")

def button2_callback(channel):
  print("Button 2 callback")

def button3_callback(channel):
  print("Button 3 callback")

def button4_callback(channel):
  print("Button 4 callback")

def button5_callback(channel):
  print("Button 5 callback")

def button6_callback(channel):
  print("Button 6 callback")




GPIO.add_event_detect(9, GPIO.RISING, callback=button1_callback)  
GPIO.add_event_detect(10, GPIO.RISING, callback=button2_callback)
GPIO.add_event_detect(11, GPIO.RISING, callback=button3_callback)
GPIO.add_event_detect(12, GPIO.RISING, callback=button4_callback)
GPIO.add_event_detect(13, GPIO.RISING, callback=button5_callback)
GPIO.add_event_detect(16, GPIO.RISING, callback=button6_callback)

while True:
  time.sleep(0.2)
