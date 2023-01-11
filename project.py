import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from gpiozero import LED
from time import sleep
import RPi.GPIO as GPIO

import time
import board
import adafruit_dht
import psutil

import pymongo
from pymongo import MongoClient

from bson.objectid import ObjectId

# Customize the Rasberry pi ports
led1 = LED(18)
led2= LED(24)
led3= LED(20)
fan = 21
motor = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(fan , GPIO.OUT)
GPIO.setup(motor , GPIO.OUT)

# Connect MONGODB string
CONNECTION_STRING = "Your Connection String here"

cluster = MongoClient(CONNECTION_STRING)

db = cluster['Raspberrypi']
collection = db['components']

results = collection.find_one({'name' :'LED'} )
print(results.get('led3'))


# Create A Collection
# post = {'name' : 'LED' , 'value' : False}
# collection.insert_one(post)

# post = {'name' : 'LED' , 'value' : False , 'led2' : False , 'led3': False , 'fan' : False , 'motor' : False , 'tempArray' : [] , 'humidArray' : []}
# collection.insert_one(post)

# DHT11 Sensor Code
for proc in psutil.process_iter():
    if proc.name() == 'libgpiod_pulsein' or proc.name() == 'libgpiod_pulsei':
        proc.kill()
sensor = adafruit_dht.DHT11(board.D23)

while True:
    results = collection.find_one({'name' :'LED'} )
    LEDstatus = results.get('value')
    led2Status = results.get('led2')
    led3Status = results.get('led3')
    fanStatus = results.get('fan')
    motorStatus = results.get('motor')

    # if(motorStatus):
    #     GPIO.output(motor , True)
    # else:
    #     GPIO.output(motor , False)

    if(fanStatus):
        GPIO.output(fan , True)
    else:
        GPIO.output(fan , False)

    if(LEDstatus):
        led1.on()
    else :
        led1.off()

    if(led2Status):
        led2.on()
    else :
        led2.off()

    if(led3Status):
        led3.on()
    else :
        led3.off()

    try:
        tempResults = collection.find_one({'_id': ObjectId('6354f43eac46ee1e99f25de3')})
        tempArray = tempResults.get('tempArray')
        humidArray = tempResults.get('humidArray')

        count = 0
        hCount = 0

        for results in tempArray:
            count += 1

        for item in humidArray:
            hCount += 1

        if(count > 20):
            collection.update_one({'_id': ObjectId('6354f43eac46ee1e99f25de3')},{'$pop' :{'tempArray' : -1}})

        if(hCount > 20):
            collection.update_one({'_id': ObjectId('6354f43eac46ee1e99f25de3')},{'$pop' :{'humidArray' : -1}})

        temp = sensor.temperature
        humidity = sensor.humidity
        print("Temperature: {}*C   Humidity: {}% ".format(temp, humidity))

        collection.update_one({'_id': ObjectId('6354f43eac46ee1e99f25de3')},
        {'$push' : {'tempArray' : temp}})

        collection.update_one({'_id': ObjectId('6354f43eac46ee1e99f25de3')},
        {'$push' : {'humidArray' : humidity}})
        
    except RuntimeError as error:
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        sensor.exit()
        raise error
    time.sleep(2.0)

