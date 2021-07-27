// Import required libraries
#include "EspMQTTClient.h"
#include <SparkFun_ADXL345.h>
#include <Arduino.h>
#include <Wire.h>
#include <dummy.h> //for esp32

/*********** COMMUNICATION SELECTION ***********/
ADXL345 adxl_1 = ADXL345();

/****************** VARIABLES ******************/
/*                                             */
int AccelMinX = 0;
int AccelMaxX = 0;
int AccelMinY = 0;
int AccelMaxY = 0;
int AccelMinZ = 0;
int AccelMaxZ = 0;

int diffX = 0;
int diffY = 0;
int diffZ = 0;

int vib_count = 0;
int quadrant_count = 0;

/****************** THRESHOLD VALUES ******************/
/*                                                    */
int ThresholdX = 100;
int ThresholdY = 50;


bool is_vibrating(int diffX, int diffY, int diffZ)
{
  return (diffX > ThresholdX && diffY > ThresholdY /*&& diffZ > ThresholdZ[sensor]*/);
}

/************** NETWORK + AWS SETUP **************/
/*                                               */
EspMQTTClient client(
  "i",
  "isaacsng",
  "broker.emqx.io",  // MQTT Broker server ip
  "",   // Can be omitted if not needed
  "",   // Can be omitted if not needed
  "laundrobot_pub"      // Client name that uniquely identify your device
);
char prev_data = '0';
char curr_data = '0';
char payload;

void onConnectionEstablished() {
}

void setup() {
  // Serial port for debugging purposes
  Serial.begin(115200);
  client.enableDebuggingMessages(); // Enable debugging messages sent to serial output
  client.enableHTTPWebUpdater(); // Enable the web updater. User and password default to values of MQTTUsername and MQTTPassword. These can be overrited with enableHTTPWebUpdater("user", "password").

  //*************INITIALIZING FIRST SENSOR*******************************
  adxl_1.powerOn();
  adxl_1.setRangeSetting(2);
  //**********************************************************************
}

/********************* MAIN CODE ******************************/
/*       Accelerometer Readings + Upload to AWS               */
void loop() {
  client.loop();
  int x, y, z;       // init variables hold results
  static uint32_t previousTime = 0;
  uint32_t currentTime = millis();

  /*********  Triggers every 15 secs  *************/
  /*                                              */
  if ( currentTime - previousTime >= 5000)
  {
    previousTime = currentTime;
    quadrant_count++; //Increment Minute Counter

    /************** Check for vibrations  *********/
    /*                                            */
    if (is_vibrating(diffX, diffY, diffZ))
      vib_count++;


    // Debugging

    Serial.print(diffX); Serial.print("  "); Serial.print(diffY); Serial.print("  "); Serial.print(diffZ); Serial.print("  VC:"); Serial.print(vib_count); Serial.print("  QC:"); Serial.print(quadrant_count);
    Serial.println();

    /*********  Triggers every 1 minute  *************/
    /*                                               */
    if (quadrant_count == 4)
    {

      if (vib_count == 4)
      {
        curr_data = '1';
      }
      else
      {
        curr_data = '0';
      }



      /*************** Initialise Payload ***************/
      /*                                                */

      if (curr_data == '1' && prev_data == '0')
      {
        payload = '1';
      }

      /*************** Upload to MQTT ***************/
      /*                                            */

      Serial.println();
      Serial.print("Published: ");
      Serial.print(payload);

      Serial.println();


      /*************** Reset Values   ***************/
      /*                                            */
      quadrant_count = 0;  // Reset minute counter
      vib_count = 0;       // Reset vibration counter
      payload = '0';         // Reset Payload
      prev_data = curr_data;

    }

    /************** Reset Values  *****************/
    /*                                            */
    for (int i = 0; i < 4; i++)
    {
      AccelMinX = 0;
      AccelMaxX = 0;
      AccelMinY = 0;
      AccelMaxY = 0;
      AccelMinZ = 0;
      AccelMaxZ = 0;
    }

  }

  /******************   Main Loop   ******************/
  /*                                                 */
  // Get the Accelerometer Readings
  adxl_1.readAccel(&x, &y, &z);

  if (x < AccelMinX) AccelMinX = x;
  if (x > AccelMaxX) AccelMaxX = x;

  if (y < AccelMinY) AccelMinY = y;
  if (y > AccelMaxY) AccelMaxY = y;

  if (z < AccelMinZ) AccelMinZ = z;
  if (z > AccelMaxZ) AccelMaxZ = z;

  // Calculating Difference in Values for X, Y and Z
  diffX = AccelMaxX - AccelMinX;
  diffY = AccelMaxY - AccelMinY;
  diffZ = AccelMaxZ - AccelMinZ;

}
