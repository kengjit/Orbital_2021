// Import required libraries
#include <AWS_IOT.h>
#include "WiFi.h"
#include <Time.h>
#include <TimeLib.h>
#include <SparkFun_ADXL345.h>

/*********** COMMUNICATION SELECTION ***********/
/*    Comment Out The One You Are Not Using    */
ADXL345 adxl = ADXL345();             // Use when you need I2C

time_t t;

/************** NETWORK + AWS SETUP **************/
/*                                             */
AWS_IOT hornbill;   // AWS_IOT instance
const char* ssid = "dlink-D8EA"; //Replace with your WiFi Name
const char* password = "bootl72707"; // Replace with your WiFi Password
char HOST_ADDRESS[] = "ah0mtuita99jn-ats.iot.us-west-2.amazonaws.com"; //Replace with your AWS Custom endpoint Address

char CLIENT_ID[] = "ADXL345_DATA";
char TOPIC_NAME[] = "ESP32/ADXL345_DATA";
int status = WL_IDLE_STATUS;
char payload[512];


void setup() {
  // Serial port for debugging purposes
  Serial.begin(115200);

  /************** ADXL345 SETUP **************/
  /*                                         */
  adxl.powerOn();                     // Power on the ADXL345

  adxl.setRangeSetting(2);           // Give the range settings
  // Accepted values are 2g, 4g, 8g or 16g
  // Higher Values = Wider Measurement Range
  // Lower Values = Greater Sensitivity

  /************** WIFI + AWS SETUP **************/
  /*                                         */
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }

  Serial.println("Connected to wifi");

  // Print ESP32 Local IP Address
  Serial.println(WiFi.localIP());

  if (hornbill.connect(HOST_ADDRESS, CLIENT_ID) == 0) // Connect to AWS using Host Address and Client ID
  {
    Serial.println("Connected to AWS");
    delay(1000);
  }
  else
  {
    Serial.println("AWS connection failed, Check the HOST Address");
    while (1);
  }
}


/********************* MAIN CODE ******************************/
/*       Accelerometer Readings + Upload to AWS               */
void loop() {
  /************* Accelerometer Readings ************/
  /*                                               */
  int x, y, z;       // init variables hold results
  adxl.readAccel(&x, &y, &z);         // Read the accelerometer values and store them in variables declared above x,y,z
  
  t = now();         // init Time
  static uint32_t previousTime = 0;
  uint32_t currentTime = millis();

  /*********  Triggers every 15 secs  *************/
  /*                                              */
  if ( currentTime - previousTime >= 5000)
  {
    previousTime = currentTime;

    /************** Check for vibrations  *********/
    /*                                            */

    // Debugging
    Serial.print("["); Serial.print(minute(t)); Serial.print(":"); Serial.print(second(t)); Serial.print("] ");
    Serial.print(x); Serial.print("  "); Serial.print(y); Serial.print("  "); Serial.print(z);
    Serial.println();

    sprintf(payload, "%i  %i  %i", x, y, z); // Create the payload for publishing

    if (hornbill.publish(TOPIC_NAME, payload) == 0) // Publish the message
    {
      Serial.print("Publish Message:");
      Serial.println(payload);
    }
    else
    {
      Serial.println("Publish failed");
    }
  }
}
