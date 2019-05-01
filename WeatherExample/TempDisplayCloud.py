#!/usr/bin/env python

# This is a demo program to push weather data temperature, humidity, pressure, co2, TVOC and push to adafruit io

'''
Copyright [2017] [Nanomesher Limited - www.nanomesher.com]

Licensed under the Apache License, Version 2.0 (the "License"); you may not use$

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed$
'''


from __future__ import unicode_literals
from time import sleep
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
from PIL import ImageFont
from subprocess import *
from Adafruit_CCS811 import Adafruit_CCS811
from Adafruit_SHT31 import *
import Adafruit_BMP.BMP085 as BMP085
import os
import time
import urllib
import urllib2


ccs =  Adafruit_CCS811()

while not ccs.available():
	pass
temp = ccs.calculateTemperature()
ccs.tempOffset = temp - 25.0


serial = i2c(port=1, address=0x3C)

#Adafruit IO keys and urls
aiokey = "YOUR ADAFRUIT IO KEY"
tempurl = 'https://io.adafruit.com/api/feeds/temp-loc1/data'
humurl = 'https://io.adafruit.com/api/feeds/hum-loc1/data'
co2url = 'https://io.adafruit.com/api/feeds/co2-loc1/data'
presurl = 'https://io.adafruit.com/api/feeds/pres-loc1/data'
tvocurl = 'https://io.adafruit.com/api/feeds/tvoc-loc1/data'


def GetLANIP():
   try:
     cmd = "ip addr show eth0 | grep inet  | grep -v inet6 | awk '{print $2}' | cut -d '/' -f 1"
     p = Popen(cmd, shell=True, stdout=PIPE)
     output = p.communicate()[0]
     ip = output[:-1]
     if(ip ==""):
	return "-"
     else:
        return ip
   except:
     return "-"

def GetWLANIP():
   try:
     cmd = "ip addr show wlan0 | grep inet  | grep -v inet6 | awk '{print $2}' | cut -d '/' -f 1"
     p = Popen(cmd, shell=True, stdout=PIPE)
     output = p.communicate()[0]
     ip = output[:-1]
     if(ip ==""):
        return "-"
     else:
        return ip
   except:
     return "-"

def make_font(name, size):
    font_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../fonts', name))
    return ImageFont.truetype(font_path, size)

def uploadData(url,data):
    dataenc = urllib.urlencode(data)
    req3 = urllib2.Request(url, dataenc)
    req3.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    req3.add_header('x-aio-key', aiokey)
    response3 = urllib2.urlopen(req3)

try:
	device = sh1106(serial, rotate=0)
	#device = ssd1306(serial, rotate=0)
	
	hasOLED = True
except:
	hasOLED = False

font1 = make_font("code2000.ttf",12)

sensor = SHT31(address = 0x44)
sensorBMP = BMP085.BMP085()
#print 'Temp             = {0:0.3f} deg C'.format(degrees)
#print 'Humidity         = {0:0.2f} %'.format(humidity)



if ccs.available():
  temp = ccs.calculateTemperature()
  if not ccs.readData():
    print "Initial CO2: ", ccs.geteCO2(), "ppm, TVOC: ", ccs.getTVOC(), " temp: ", temp


degrees=0
humidity=0
co2=0
tvoc=0

while(True):
  degrees = round(sensor.read_temperature(),1)
  humidity = round(sensor.read_humidity(),1)
  pressure = sensorBMP.read_pressure()/100.0

  tempst = '{0:0.3f}C'.format(degrees)
  humidst = '{0:0.2f}%'.format(humidity)
  pressurest = '{0:0.2f} hPa'.format(pressure)
  with canvas(device) as draw:
    draw.text((5, 2), "Pi Weather Monitor", font=font1, fill="white")
    draw.text((1, 16), tempst + "/" + humidst, font=font1, fill="white")
    draw.text((1, 32), pressurest, font=font1, fill="white")
    if ccs.available():
      temp = ccs.calculateTemperature()
      if not ccs.readData():
        co2 = ccs.geteCO2()
        tvoc = ccs.getTVOC()
        draw.text((1, 48), str(co2) + "ppm VOC:" + str(tvoc), font=font1, fill="white")


  degreesval = {'value': degrees}
  humidityval = {'value': humidity}
  pressureval = {'value': pressure}
  co2val = {'value': co2}
  tvocval = {'value': tvoc}

  uploadData(humurl,humidityval)
  uploadData(tempurl,degreesval)
  uploadData(presurl,pressureval)
  uploadData(co2url,co2val)
  uploadData(tvocurl, tvocval)

  sleep(10)
  sensor.clear_status()

	
	

