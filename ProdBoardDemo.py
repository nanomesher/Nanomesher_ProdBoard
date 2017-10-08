import  RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(10, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(9, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(11, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
#Toggle for LED2
toggle2 = False
toggle1 = False
while True:
    inputValue2 = GPIO.input(10)
    inputValue1 = GPIO.input(9)
    
    inputValue3 = GPIO.input(11)

    inputValue4 = GPIO.input(12)

    inputValue5 = GPIO.input(13)

    inputValue6 = GPIO.input(16)

    if (inputValue3 == True):
        print("Button 3 press")

    if (inputValue4 == True):
        print("Button 4 press")

    if (inputValue5 == True):
        print("Button 5 press")

    if (inputValue6 == True):
        print("Button 6 press")



    if (inputValue2 == True):
        print("Button 2 press ")
        if(toggle2 == False):
            GPIO.output(5,GPIO.HIGH)
            print("H")
            toggle2 = True
        else:
            GPIO.output(5,GPIO.LOW)
            print("L")
            toggle2 = False	

    if (inputValue1 == True):
        print("Button 1 press ")
        
        if(toggle1 == False):
            GPIO.output(26,GPIO.HIGH)
            print("H")
            toggle1 = True
        else:
            GPIO.output(26,GPIO.LOW)
            print("L")
            toggle1 = False

    time.sleep(0.2)
