'''
Copyright [2017] [Nanomesher Limited - www.nanomesher.com]

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
'''


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

