#!/usr/bin/env python
# This is a demo to show ip address of eth0 and wlan0 network interace on the ProdBoard OLED Display

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
import sys
import ConfigParser
import WeatherDataAccess
import urllib
import urllib2
import logging


ccs =  Adafruit_CCS811()

while not ccs.available():
	pass
temp = ccs.calculateTemperature()
ccs.tempOffset = temp - 25.0


serial = i2c(port=1, address=0x3C)

config = ConfigParser.ConfigParser()
config.read('AirMonitor.config')

SaveToDB = False
SaveToDBInt = 60
LastSaveToDB = 0

SendToAIO = False
SendToAIOInt = 60
LastSendToAIO = 0

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('piairmon.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


if(config.get('DEFAULT','SaveToDatabase')=='yes'):
    SaveToDB = True
    SaveToDBInt = int(config.get('DEFAULT','SaveToDatabaseIntervalSecond'))

if(config.get('DEFAULT','SendToAIO')=='yes'):
    SendToAIO = True
    SendToAIOInt = int(config.get('DEFAULT','SendToAIOIntervalSecond'))
    AIOKey = config.get('AIO','AIOKey')
    tempurl = config.get('AIO','Tempurl')
    humurl = config.get('AIO','Humurl')
    co2url = config.get('AIO','Co2url')
    presurl = config.get('AIO','Presurl')
    tvocurl = config.get('AIO','Tvocurl')

def uploadData(url,data):
    dataenc = urllib.urlencode(data)
    req3 = urllib2.Request(url, dataenc)
    req3.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    req3.add_header('x-aio-key', AIOKey)
    response3 = urllib2.urlopen(req3)


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



degrees=0
humidity=0
logger.info('Nanomesher Pi Air Mon started')

while(True):
 try:
  sleep(1)
  degrees = sensor.read_temperature()
  humidity = sensor.read_humidity()
  temp = '{0:0.3f}C'.format(degrees)
  humid = '{0:0.2f} %'.format(humidity)
  pressure = '{0:0.2f} hPa'.format(sensorBMP.read_pressure()/100.0)  
  with canvas(device) as draw:
    draw.text((5, 2), "Nanomesher Air Mon",font=font1, fill="white")
    draw.text((1, 18), temp + "/" + humid,font=font1, fill="white")
    draw.text((1, 36), pressure,font=font1, fill="white")
    if ccs.available():
      temp = ccs.calculateTemperature()
      if not ccs.readData():
        co2 = ccs.geteCO2()
        tvoc = ccs.getTVOC()
        draw.text((1, 48), str(co2) + "ppm VOC:" + str(tvoc), font=font1, fill="white")

    curtime = time.time()
    if(SaveToDB and ((curtime-LastSaveToDB)>=(SaveToDBInt-1))):
      LastSaveToDB = curtime
      WeatherDataAccess.InsertWeatherData(27, 51, 979, 441, 5)

    if(SendToAIO and ((curtime-LastSendToAIO)>=(SendToAIOInt-1))):
      LastSendToAIO = curtime
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
  sensor.clear_status()
 except Exception as e:
  logger.error(e)








	
	

