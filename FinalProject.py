import gspread
from oauth2client.service_account import ServiceAccountCredentials
import _thread
from twython import Twython
import time
import random
import blynklib
import smbus

## API KEYS AND ACCESS TOKEN ##
API_KEY = 'YOUR_GG_API_KEY'
API_SECRET = 'YOUR_API_SECRET'
ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
ACCESS_SECRET = 'YOUR_ACCESS_SECRET'

## TwitterAPI ##
api = Twython(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

## our tweets default template ##
TEMP_TWEET = " The temperature is getting weird. Do something human! Temperature: "
HUM_TWEET = " The humidity is something else. And my plants don't like it. HELP! Humidity level: "
MOIST_TWEET = " Soil moisture level is not ideal, human wtf? Soil moisture percent: "

## Conditional values ##
## temp 15-24, hum 30-60, moist 40-60
MAX_TEMP = 40
MIN_TEMP = 5

MAX_HUM = 80
MIN_HUM = 10

MAX_MOIST = 90
MIN_MOIST = 10
##these values are all general range that most plants prefer

## Introduce a scope to hook up our credentials ##
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

## Confirm our credentials from the json key file ##
creds = ServiceAccountCredentials.from_json_keyfile_name("YOUR_CRED_FILE.json", scope)

## create a client and authorize ## 
client = gspread.authorize(creds)

## get our data sheet ##
sheet = client.open("gardenStatus").sheet1

## return the index of the last valid row
def lastAvailableRow(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return (len(str_list))

## Number of valid rows ##
lastValidRow = lastAvailableRow(sheet)

## check for new entry and change the index
def isNewEntry(worksheet):
    global lastValidRow
    if lastAvailableRow(worksheet) > lastValidRow:
        lastValidRow = lastAvailableRow(worksheet)
        return True
    else:
        return False

## Function to get the value from last row
def getAttriFromLastRow():
    valuesList = sheet.row_values(lastValidRow)
    return float(valuesList[0]), float(valuesList[1]), float(valuesList[2])

## check the status of our attribute and return a flag if it's not acceptable
def checkStatus(attri, ATTRI_MAX, ATTRI_MIN):
    if (attri >= ATTRI_MAX or attri <= ATTRI_MIN):
        return (attri, False)
    else:
        return (attri, True)
 ## try to make a Tweet if the flag is false   
def tryTweet(attri, ATTRI_MAX, ATTRI_MIN, ATTRI_TEMP):
    # generate a 6-digit number to avoid tweets duplication
    random.seed(time.process_time())
    randID = random.randint(100000, 999999)
    
    attri, flag = checkStatus(attri, ATTRI_MAX, ATTRI_MIN)
    # make tweets accordingly
    if flag == False:
        TWEET = str(randID) + ATTRI_TEMP + str(attri)
        api.update_status(status = TWEET)
        print("Tweeted: " + TWEET)

## create a function to check the status of our garden
def checkGardenStatus():
    while True:
        if(isNewEntry(sheet)):
            print(lastValidRow)
            hum, temp, moist = getAttriFromLastRow()
            tryTweet(temp, MAX_TEMP, MIN_TEMP, TEMP_TWEET)
            tryTweet(hum, MAX_HUM, MIN_HUM, HUM_TWEET)
            tryTweet(moist, MAX_MOIST, MIN_MOIST, MOIST_TWEET)
        else:
            print(lastValidRow)
        time.sleep(30)

## initialise our bus channel ##
channel = 1

## Enter our slave address ##
address = 0x08

## initalise our bus ##
bus = smbus.SMBus(channel)

## create your blynk auth token ##
BLYNK_AUTH = 'YOUR_BLYNK_AUTH'

## start your blink ##
blynk = blynklib.Blynk(BLYNK_AUTH)

## a flag to our LED ##
ledIsOn = False

## handler the event from our Blynk App ##
@blynk.handle_event('write V4')
def read_virtual_pin_handler(pin, value):
    global ledIsOn
    ## sending bytes to our slave Argon 
    if value[0] == '0':
        print("OFF")
        bus.write_byte(address, 0)
        ledIsOn = False
    else:
        print("ON")
        bus.write_byte(address, 1)
        ledIsOn = True
        
 ## define a function to run our blynk ##
def runBlynk():
    while True:
        blynk.run()

try:
    _thread.start_new_thread(checkGardenStatus, ())
    _thread.start_new_thread(runBlynk,())
    
except KeyboardInterrupt:
    print("Quit requested")


