#
# CCS811_RPi class usage example
#
# Petr Lukas
# July, 11 2017
#
# Version 1.0

import time
import urllib2 # comment this line if you don't need ThinkSpeak connection
import SDL_Pi_HDC1000 # comment this line if you don't use HDC sensor

from CCS811_RPi import CCS811_RPi

ccs811 = CCS811_RPi()

# Do you want to send data to thingSpeak? If yes set WRITE API KEY, otherwise set False
THINGSPEAK      = False # or type 'YOURAPIKEY'

# Do you want to preset sensor baseline? If yes set the value here, otherwise set False
INITIALBASELINE = False

# Do you want to use integrated temperature meter to compensate temp/RH (CJMCU-8118 board)?
# If not pre-set sensor compensation temperature is 25 C and RH is 50 %
# You can compensate manually by method ccs811.setCompensation(temperature,humidity) 
HDC1080         = False

'''
MEAS MODE REGISTER AND DRIVE MODE CONFIGURATION
0b0       Idle (Measurements are disabled in this mode)
0b10000   Constant power mode, IAQ measurement every second
0b100000  Pulse heating mode IAQ measurement every 10 seconds
0b110000  Low power pulse heating mode IAQ measurement every 60
0b1000000 Constant power mode, sensor measurement every 250ms
'''
# Set MEAS_MODE (measurement interval)
configuration = 0b100000

# Set read interval for retriveving last measurement data from the sensor
pause = 60

def thingSpeak(eCO2,TVOC,baseline,temperature,humidity):
    print 'Sending to ThingSpeak API...'
    url = "https://api.thingspeak.com/update?api_key="
    url += THINGSPEAK
    url += "&field1="
    url += str(eCO2)
    url += "&field2="
    url += str(TVOC)
    url += "&field3="
    url += str(baseline)
    url += "&field4="
    url += str(temperature)
    url += "&field5="
    url += str(humidity)
    #print url
    try: 
      content = urllib2.urlopen(url).read()
    except urllib2.HTTPError:
      print "Invalid HTTP response"
      return False
    print 'Done'
    #print content



print 'Checking hardware ID...'
hwid = ccs811.checkHWID()
if(hwid == hex(129)):
        print 'Hardware ID is correct'
else: print 'Incorrect hardware ID ',hwid, ', should be 0x81'




#print 'MEAS_MODE:',ccs811.readMeasMode()
ccs811.configureSensor(configuration)
print 'MEAS_MODE:',ccs811.readMeasMode()
print 'STATUS: ',bin(ccs811.readStatus())
print '---------------------------------'

# Use these lines if you need to pre-set and check sensor baseline value
if(INITIALBASELINE > 0):
        ccs811.setBaseline(INITIALBASELINE)
        print(ccs811.readBaseline())


# Use these lines if you use CJMCU-8118 which has HDC1080 temp/RH sensor
if(HDC1080):
        hdc1000 = SDL_Pi_HDC1000.SDL_Pi_HDC1000()
        hdc1000.turnHeaterOff()
        hdc1000.setTemperatureResolution(SDL_Pi_HDC1000.HDC1000_CONFIG_TEMPERATURE_RESOLUTION_14BIT)
        hdc1000.setHumidityResolution(SDL_Pi_HDC1000.HDC1000_CONFIG_HUMIDITY_RESOLUTION_14BIT)


while(1):
        if(HDC1080):
                humidity = hdc1000.readHumidity()
                temperature = hdc1000.readTemperature()
                ccs811.setCompensation(temperature,humidity)
        else:
                humidity = 50.00
                temperature = 25.00
        
        statusbyte = ccs811.readStatus()
        print 'STATUS: ', bin(statusbyte)

        error = ccs811.checkError(statusbyte)
        if(error):
                print 'ERROR:',ccs811.checkError(statusbyte)
                
        if(not ccs811.checkDataReady(statusbyte)):
                print 'No new samples are ready'
                print '---------------------------------';
                time.sleep(pause)
                continue;
        result = ccs811.readAlg();
        if(not result):
                #print 'Invalid result received'
                time.sleep(pause)
                continue;
        baseline = ccs811.readBaseline()
        print 'eCO2: ',result['eCO2'],' ppm'
        print 'TVOC: ',result['TVOC'], 'ppb'
        print 'Status register: ',bin(result['status'])
        print 'Last error ID: ',result['errorid']
        print 'RAW data: ',result['raw']
        print 'Baseline: ',baseline
        print '---------------------------------';

        if (THINGSPEAK is not False):
                thingSpeak(result['eCO2'],result['TVOC'],baseline,temperature,humidity)
        time.sleep(pause)



 CCS811_RPi.py
#
# CCS811_RPi
#
# Petr Lukas
# July, 11 2017
#
# Version 1.0

import struct, array, time, io, fcntl

# I2C Address
CCS811_ADDRESS =  (0x5A)

# Registers
CCS811_HW_ID            =  (0x20)
CSS811_STATUS           =  (0x00)
CSS811_APP_START        =  (0xF4)
CSS811_MEAS_MODE        =  (0x01)
CSS811_ERROR_ID         =  (0xE0)
CSS811_RAW_DATA         =  (0x03)
CSS811_ALG_RESULT_DATA  =  (0x02)
CSS811_BASELINE         =  (0x11)
CSS811_ENV_DATA         =  (0x05)

# Errors ID
ERROR = {}
ERROR[0] = 'WRITE_REG_INVALID'
ERROR[1] = 'READ_REG_INVALID'
ERROR[2] = 'MEASMODE_INVALID'
ERROR[3] = 'MAX_RESISTANCE'
ERROR[4] = 'HEATER_FAULT'
ERROR[5] = 'HEATER_SUPPLY'

I2C_SLAVE=0x0703

CCS811_fw= 0
CCS811_fr= 0

class CCS811_RPi:
        def __init__(self, twi=1, addr=CCS811_ADDRESS ):
                global CCS811_fr, CCS811_fw
                
                CCS811_fr= io.open("/dev/i2c-"+str(twi), "rb", buffering=0)
                CCS811_fw= io.open("/dev/i2c-"+str(twi), "wb", buffering=0)

                # set device address
                fcntl.ioctl(CCS811_fr, I2C_SLAVE, CCS811_ADDRESS)
                fcntl.ioctl(CCS811_fw, I2C_SLAVE, CCS811_ADDRESS)
                time.sleep(0.015)


        # public functions
        def checkHWID(self):
                s = [CCS811_HW_ID] # Hardware ID
                s2 = bytearray( s )
                CCS811_fw.write( s2 )
                time.sleep(0.0625)

                data = CCS811_fr.read(1)
       
                buf = array.array('B', data)
                return hex(buf[0])

        
        def readStatus(self):
                time.sleep(0.015)

                s = [CSS811_STATUS]
                s2 = bytearray( s )
                CCS811_fw.write( s2 )
                time.sleep(0.0625)              

                data = CCS811_fr.read(1)
                buf = array.array('B', data)
                return buf[0]

        def checkError(self,status_byte):
                time.sleep(0.015)
                error_bit = ((status_byte) >> 0) & 1
                if(not error_bit):
                        return False

                s = [CSS811_ERROR_ID]
                s2 = bytearray( s )
                CCS811_fw.write( s2 )
                time.sleep(0.0625)              

                data = CCS811_fr.read(1)
                buf = array.array('B', data)
                return ERROR[int(buf[0])]
        
        def configureSensor(self, configuration):
                # Switch sensor to application mode
                s = [CSS811_APP_START]
                s2 = bytearray( s )
                CCS811_fw.write( s2 )
                time.sleep(0.0625)

                s = [CSS811_MEAS_MODE,configuration,0x00]
                s2 = bytearray( s )
                CCS811_fw.write( s2 )
                time.sleep(0.015)
                return

        def readMeasMode(self):
                time.sleep(0.015)
                s = [CSS811_MEAS_MODE]
                s2 = bytearray( s )
                CCS811_fw.write( s2 )
                time.sleep(0.0625)              

                data = CCS811_fr.read(1)
                buf = array.array('B', data)
                return bin(buf[0])

        def readRaw(self):
                time.sleep(0.015)
                s = [CSS811_RAW_DATA]
                s2 = bytearray( s )
                CCS811_fw.write( s2 )
                time.sleep(0.0625)              

                data = CCS811_fr.read(2)
                buf = array.array('B', data)
                return (buf[0]*256 + buf[1])

        def readAlg(self):
                time.sleep(0.015)
                s = [CSS811_ALG_RESULT_DATA]
                s2 = bytearray( s )
                CCS811_fw.write( s2 )
                time.sleep(0.0625)              

                data = CCS811_fr.read(8)
                buf = array.array('B', data)
                result = {}
                # Read eCO2 value and check if it is valid
                result['eCO2'] = buf[0]*256 + buf[1]
                if(result['eCO2'] > 8192):
                        print 'Invalid eCO2 value'
                        return False
                # Read TVOC value and check if it is valid
                result['TVOC'] = buf[2]*256 + buf[3]
                if(result['TVOC'] > 1187):
                        print 'Invalid TVOC value'
                        return False
                
                result['status'] = buf[4]

                # Read the last error ID and check if it is valid
                result['errorid'] = buf[5]
                if(result['errorid'] > 5):
                        print 'Invalid Error ID'
                        return False
                        
                result['raw'] = buf[6]*256 + buf[7]
                return result

        def readBaseline(self):
                time.sleep(0.015)
                s = [CSS811_BASELINE]
                s2 = bytearray( s )
                CCS811_fw.write( s2 )
                time.sleep(0.0625)              

                data = CCS811_fr.read(2)
                buf = array.array('B', data)
                return (buf[0]*256 + buf[1])

        def checkDataReady(self, status_byte):
                ready_bit = ((status_byte) >> 3) & 1
                if(ready_bit):
                        return True
                else: return False

        def setCompensation(self, temperature, humidity):
                temperature = round(temperature,2)
                humidity = round(humidity,2)
                print 'Setting compensation to ',temperature,' C and ',humidity,' %'
                hum1 = int(humidity//0.5)
                hum2 = int(humidity*512-hum1*256)

                temperature = temperature+25
                temp1 = int(temperature//0.5)
                temp2 = int(temperature*512-temp1*256)

                s = [CSS811_ENV_DATA,hum1,hum2,temp1,temp2,0x00]
                s2 = bytearray( s )
                CCS811_fw.write( s2 )
                
                return

        def setBaseline(self, baseline):
                print 'Setting baseline to ',baseline
                buf = [0,0]
                s = struct.pack('>H', baseline)
                buf[0], buf[1] = struct.unpack('>BB', s)
                print buf[0]
                print buf[1]
                
                s = [CSS811_BASELINE,buf[0],buf[1],0x00]
                s2 = bytearray( s )
                CCS811_fw.write( s2 )
                time.sleep(0.015)
 SDL_Pi_HDC1000.py
#
# SDL_Pi_HDC1000
# Raspberry Pi Driver for the SwitchDoc Labs HDC1000 Breakout Board
#
# SwitchDoc Labs
# January 2017
#
# Version 1.1

#constants

# I2C Address
HDC1000_ADDRESS =                       (0x40)    # 1000000 
# Registers
HDC1000_TEMPERATURE_REGISTER =          (0x00)
HDC1000_HUMIDITY_REGISTER =             (0x01)
HDC1000_CONFIGURATION_REGISTER =        (0x02)
HDC1000_MANUFACTURERID_REGISTER =       (0xFE)
HDC1000_DEVICEID_REGISTER =         (0xFF)
HDC1000_SERIALIDHIGH_REGISTER =         (0xFB)
HDC1000_SERIALIDMID_REGISTER =          (0xFC)
HDC1000_SERIALIDBOTTOM_REGISTER =       (0xFD)



#Configuration Register Bits

HDC1000_CONFIG_RESET_BIT =              (0x8000)
HDC1000_CONFIG_HEATER_ENABLE =          (0x2000)
HDC1000_CONFIG_ACQUISITION_MODE =       (0x1000)
HDC1000_CONFIG_BATTERY_STATUS =         (0x0800)
HDC1000_CONFIG_TEMPERATURE_RESOLUTION = (0x0400)
HDC1000_CONFIG_HUMIDITY_RESOLUTION_HBIT =    (0x0200)
HDC1000_CONFIG_HUMIDITY_RESOLUTION_LBIT =    (0x0100)

HDC1000_CONFIG_TEMPERATURE_RESOLUTION_14BIT = (0x0000)
HDC1000_CONFIG_TEMPERATURE_RESOLUTION_11BIT = (0x0400)

HDC1000_CONFIG_HUMIDITY_RESOLUTION_14BIT = (0x0000)
HDC1000_CONFIG_HUMIDITY_RESOLUTION_11BIT = (0x0100)
HDC1000_CONFIG_HUMIDITY_RESOLUTION_8BIT = (0x0200)

I2C_SLAVE=0x0703

import struct, array, time, io, fcntl

HDC1000_fw= 0
HDC1000_fr= 0

class SDL_Pi_HDC1000:
        def __init__(self, twi=1, addr=HDC1000_ADDRESS ):
                global HDC1000_fr, HDC1000_fw
                
                HDC1000_fr= io.open("/dev/i2c-"+str(twi), "rb", buffering=0)
                HDC1000_fw= io.open("/dev/i2c-"+str(twi), "wb", buffering=0)

                # set device address
                fcntl.ioctl(HDC1000_fr, I2C_SLAVE, HDC1000_ADDRESS)
                fcntl.ioctl(HDC1000_fw, I2C_SLAVE, HDC1000_ADDRESS)
                time.sleep(0.015) #15ms startup time

                config = HDC1000_CONFIG_ACQUISITION_MODE 

                s = [HDC1000_CONFIGURATION_REGISTER,config>>8,0x00]
                s2 = bytearray( s )
                HDC1000_fw.write( s2 ) #sending config register bytes
                time.sleep(0.015)               # From the data sheet
                
                #       0x10(48)    Temperature, Humidity enabled, Resolultion = 14-bits, Heater off
                #config = HDC1000_CONFIG_ACQUISITION_MODE 
                #self._bus.write_byte_data(HDC1000_ADDRESS,HDC1000_CONFIGURATION_REGISTER, config>>8)


        # public functions

        def readTemperature(self):
               

                s = [HDC1000_TEMPERATURE_REGISTER] # temp
                s2 = bytearray( s )
                HDC1000_fw.write( s2 )
                time.sleep(0.0625)              # From the data sheet

                data = HDC1000_fr.read(2) #read 2 byte temperature data
                buf = array.array('B', data)
                #print ( "Temp: %f 0x%X %X" % (  ((((buf[0]<<8) + (buf[1]))/65536.0)*165.0 ) - 40.0   ,buf[0],buf[1] )  )

                
                # Convert the data
                temp = (buf[0] * 256) + buf[1]
                cTemp = (temp / 65536.0) * 165.0 - 40
                return cTemp


        def readHumidity(self):
                # Send humidity measurement command, 0x01(01)
                time.sleep(0.015)               # From the data sheet

                s = [HDC1000_HUMIDITY_REGISTER] # hum
                s2 = bytearray( s )
                HDC1000_fw.write( s2 )
                time.sleep(0.0625)              # From the data sheet

                data = HDC1000_fr.read(2) #read 2 byte humidity data
                buf = array.array('B', data)
                #print ( "Humidity: %f 0x%X %X " % (  ((((buf[0]<<8) + (buf[1]))/65536.0)*100.0 ),  buf[0], buf[1] ) )
                humidity = (buf[0] * 256) + buf[1]
                humidity = (humidity / 65536.0) * 100.0
                return humidity
        
        def readConfigRegister(self):
                # Read config register


                s = [HDC1000_CONFIGURATION_REGISTER] # temp
                s2 = bytearray( s )
                HDC1000_fw.write( s2 )
                time.sleep(0.0625)              # From the data sheet

                data = HDC1000_fr.read(2) #read 2 byte config data

                buf = array.array('B', data)


                #print "register=%X %X"% (buf[0], buf[1])
                return buf[0]*256+buf[1]

       
        def turnHeaterOn(self):
                # Read config register
                config = self.readConfigRegister()
                config = config | HDC1000_CONFIG_HEATER_ENABLE 
                s = [HDC1000_CONFIGURATION_REGISTER,config>>8,0x00]
                s2 = bytearray( s )
                HDC1000_fw.write( s2 ) #sending config register bytes
                time.sleep(0.015)               # From the data sheet

                return

        def turnHeaterOff(self):
                # Read config register
                config = self.readConfigRegister()
                config = config & ~HDC1000_CONFIG_HEATER_ENABLE 
                s = [HDC1000_CONFIGURATION_REGISTER,config>>8,0x00]
                s2 = bytearray( s )
                HDC1000_fw.write( s2 ) #sending config register bytes
                time.sleep(0.015)               # From the data sheet

                return

        

        def setHumidityResolution(self,resolution):
                # Read config register
                config = self.readConfigRegister()
                config = (config & ~0x0300) | resolution 
                s = [HDC1000_CONFIGURATION_REGISTER,config>>8,0x00]
                s2 = bytearray( s )
                HDC1000_fw.write( s2 ) #sending config register bytes
                time.sleep(0.015)               # From the data sheet
                return

        def setTemperatureResolution(self,resolution):
                # Read config register
                config = self.readConfigRegister()
                config = (config & ~0x0400) | resolution 
               
                s = [HDC1000_CONFIGURATION_REGISTER,config>>8,0x00]
                s2 = bytearray( s )
                HDC1000_fw.write( s2 ) #sending config register bytes
                time.sleep(0.015)               # From the data sheet
                
                
                return

        def readBatteryStatus(self):
                
                # Read config register
                config = self.readConfigRegister()
                config = config & ~ HDC1000_CONFIG_HEATER_ENABLE

                if (config == 0):
                    return True
                else:
                    return False

                return 0


        def readManufacturerID(self):

            s = [HDC1000_MANUFACTURERID_REGISTER] # temp
            s2 = bytearray( s )
            HDC1000_fw.write( s2 )
            time.sleep(0.0625)              # From the data sheet
    
            data = HDC1000_fr.read(2) #read 2 byte config data
    
            buf = array.array('B', data)
            return buf[0] * 256 + buf[1]

        def readDeviceID(self):
    
            s = [HDC1000_DEVICEID_REGISTER] # temp
            s2 = bytearray( s )
            HDC1000_fw.write( s2 )
            time.sleep(0.0625)              # From the data sheet
    
            data = HDC1000_fr.read(2) #read 2 byte config data
    
            buf = array.array('B', data)
            return buf[0] * 256 + buf[1]

        def readSerialNumber(self):

            serialNumber = 0
    
            s = [HDC1000_SERIALIDHIGH_REGISTER] # temp
            s2 = bytearray( s )
            HDC1000_fw.write( s2 )
            time.sleep(0.0625)              # From the data sheet
            data = HDC1000_fr.read(2) #read 2 byte config data
            buf = array.array('B', data)
            serialNumber = buf[0]*256+ buf[1] 
    
            s = [HDC1000_SERIALIDMID_REGISTER] # temp
            s2 = bytearray( s )
            HDC1000_fw.write( s2 )
            time.sleep(0.0625)              # From the data sheet
            data = HDC1000_fr.read(2) #read 2 byte config data
            buf = array.array('B', data)
            serialNumber = serialNumber*256 + buf[0]*256 + buf[1] 
    
            s = [HDC1000_SERIALIDBOTTOM_REGISTER] # temp
            s2 = bytearray( s )
            HDC1000_fw.write( s2 )
            time.sleep(0.0625)              # From the data sheet
            data = HDC1000_fr.read(2) #read 2 byte config data
            buf = array.array('B', data)
            serialNumber = serialNumber*256 + buf[0]*256 + buf[1] 
    
            return serialNumber
