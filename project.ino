
// This #include statement was automatically added by the Particle IDE.
#include <MQTT.h>

// This #include statement was automatically added by the Particle IDE.
#include <Adafruit_DHT.h>

#define DHTPIN 7 //connect our DHT22 to our digital pin 7
#define DHTTYPE DHT22
#define LOG_INTERVAL 60000 //delay for 1 minutes

DHT dht(DHTPIN, DHTTYPE);

const int DRY_VALUE = 3520; //max value the sensor take when it's completely dry
const int SUB_VALUE = 2000; //max value when submerged in water
const char *FIELD_SEPERATOR = "|||";
const char *EVENT_NAME = "gardenStatus";

//init our values
int LED = D6;
int soilMoistPer;
int soilMoist;
float hum;
float temp;
char buffer[256];

//declare our capacitive soil moisture sensor pin
int soilSen = A0;

//init error counter
int errCount = 0;

void setup() {
    //begin serial for dubugging 
    Serial.begin(9600);
    //begin our dht22
    dht.begin();
    //print out header for serial com
    Serial.println("millis, hum, temp, moistPer");
    
    //init our capacitive soil moisture module
    pinMode(A0, INPUT);
    
    //establish an I2C communication aand enter as a slave
    Wire.begin(0x08);
    
    //when we receive information from the master, run eventHandler
    Wire.onReceive(eventHandler);

    
    //change pin mode of our LED
    pinMode(LED, OUTPUT);
}

void loop() {
    
    //first, lets get our readings
    hum = dht.getHumidity();
    temp= dht.getTempCelcius();
    soilMoist = analogRead(soilSen);
    
    // Map our soil moister value to the Dry Value and the Submerged Value to get a percentage of soil moisture
    soilMoistPer = map(soilMoist, DRY_VALUE, SUB_VALUE, 0, 100);
    
    // time since start
    uint32_t m = millis();
    
    // This part is to monitor your results from a serial monitor
    Serial.print(m);   
    // milliseconds since start
    Serial.print(", ");
    Serial.print(hum);
    
    Serial.print(", ");
    Serial.print(temp);
    
    Serial.print(", ");
    Serial.println(soilMoistPer);
    
    // We will check our results, if it's not a valid result, we will publish an Error event
    if(isnan(hum) == 0 && isnan(temp) == 0)
    {
        snprintf(buffer, sizeof(buffer), "%.02f%s%.02f%s%d", hum, FIELD_SEPERATOR, temp, FIELD_SEPERATOR, soilMoistPer);
        Particle.publish(EVENT_NAME, buffer, PRIVATE);
        
        //reset the error count
        errCount = 0; 
    } else
    {
        
        Particle.publish("Error", "Sensor(s) not working", PRIVATE);
        errCount ++;
        
        // if there are more than x-number of consecutive error counts, publish this event
        if (errCount > 30)
        {
            Particle.publish("Critical Error", "System failed!", PRIVATE);
        }
    }
    
    // We are going to delay our program by the amount defined
    delay((LOG_INTERVAL) - (millis() % LOG_INTERVAL));
}

//function to turn on LED
void turnLED(int state)
{
    if (state == 1)
    {
        digitalWrite(LED, HIGH);
    } else if (state == 0)
    {
        digitalWrite(LED, LOW);
    }
}

//function to handler request
void eventHandler(int numBytes)
{   //read the bytes send by the master and respond accordingly
    char c = Wire.read();
    if (c == 1)
    {   //we will delegate this task to another function
        turnLED(1);
    }
    else if (c == 0)
    {
        turnLED(0);
    }
    
}

