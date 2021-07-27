// Import required libraries
#include "EspMQTTClient.h"
#include <SparkFun_ADXL345.h>
#include <Arduino.h>
#include <Wire.h>
#include <dummy.h> //for esp32

/*********** COMMUNICATION SELECTION ***********/
ADXL345 adxl_1 = ADXL345();
ADXL345 adxl_2 = ADXL345();
ADXL345 adxl_3 = ADXL345();
ADXL345 adxl_4 = ADXL345();

/****************** VARIABLES ******************/
/*                                             */
int AccelMinX[4] = {0};
int AccelMaxX[4] = {0};
int AccelMinY[4] = {0};
int AccelMaxY[4] = {0};
int AccelMinZ[4] = {0};
int AccelMaxZ[4] = {0};

int diffX[4] = {0};
int diffY[4] = {0};
int diffZ[4] = {0};

int vib_count[4] = {0};
int quadrant_count = 0;

/****************** THRESHOLD VALUES ******************/
/*                                                    */
int ThresholdX[4] = {20, 20, 100, 20};
int ThresholdY[4] = {40, 40, 50, 40};
//int ThresholdZ[4] = {240, 240, , 240};

/************** DEFINED VARIABLES **************/
/*                                             */
#define TCAADDR 0x70

/************** FUNCTIONS **********************/
/*                                             */
void tcaselect (uint8_t i) {
  if (i > 7) return;

  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
}

bool is_vibrating(int sensor, int diffX, int diffY, int diffZ)
{
  return (diffX > ThresholdX[sensor] && diffY > ThresholdY[sensor] /*&& diffZ > ThresholdZ[sensor]*/);
}

bool is_zero(char* string)
{
  for (int i = 0; i < 4; i++)
  {
    if (string[i] == '1')
    {
      return false;
    }
  }
  return true;
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
char prev_data[4] = {'0', '0', '0', '0'};
char curr_data[4] = {'0', '0', '0', '0'};
char payload[5] = {'0', '0', '0', '0'};

void onConnectionEstablished() {
}

void setup() {
  // Serial port for debugging purposes
  Serial.begin(115200);
  client.enableDebuggingMessages(); // Enable debugging messages sent to serial output
  client.enableHTTPWebUpdater(); // Enable the web updater. User and password default to values of MQTTUsername and MQTTPassword. These can be overrited with enableHTTPWebUpdater("user", "password").

  //*************INITIALIZING FIRST SENSOR*******************************
  tcaselect(0);
  adxl_1.powerOn();
  adxl_1.setRangeSetting(2);
  //**********************************************************************

  //*************INITIALIZING SECOND SENSOR*******************************
  tcaselect(1);
  adxl_2.powerOn();
  adxl_2.setRangeSetting(2);
  //**********************************************************************

  //*************INITIALIZING THIRD SENSOR*******************************
  tcaselect(2);
  adxl_3.powerOn();
  adxl_3.setRangeSetting(2);
  //**********************************************************************

  //*************INITIALIZING FOURTH SENSOR*******************************
  tcaselect(3);
  adxl_4.powerOn();
  adxl_4.setRangeSetting(2);
  //**********************************************************************
}

/********************* MAIN CODE ******************************/
/*       Accelerometer Readings + Upload to AWS               */
void loop() {
  client.loop();
  int x[4], y[4], z[4];       // init variables hold results
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
    for (int i = 0; i < 4; i++)
    {
      if (is_vibrating(i, diffX[i], diffY[i], diffZ[i]))
      {
        vib_count[i]++;
      }
    }


    // Debugging
    for (int i = 0; i < 4; i++)
    {
      Serial.print(diffX[i]); Serial.print("  "); Serial.print(diffY[i]); Serial.print("  "); Serial.print(diffZ[i]); Serial.print("  VC:"); Serial.print(vib_count[i]); Serial.print("  QC:"); Serial.print(quadrant_count);
      Serial.println();
    }

    /*********  Triggers every 1 minute  *************/
    /*                                               */
    if (quadrant_count == 4)
    {
      for (int i = 0; i < 4; i++)
      {
        if (vib_count[i] == 4)
        {
          curr_data[i] = '1';
        }
        else
        {
          curr_data[i] = '0';
        }
      }


      /*************** Initialise Payload ***************/
      /*                                                */
      for (int i = 0; i < 4; i++)
      {
        if (curr_data[i] == '1' && prev_data[i] == '0')
        {
          payload[i] = '1';
        }
      }
      /*************** Upload to MQTT ***************/
      /*                                            */
      if (!is_zero(payload))
      {
        client.publish("laundrobot", payload);
        Serial.println();
        Serial.print("Published: ");
        for (int i = 0; i < 4; i++)
        {
          Serial.print(payload[i]);
        }
        Serial.println();
      }

      /*************** Reset Values   ***************/
      /*                                            */
      quadrant_count = 0;  // Reset minute counter
      for (int i = 0; i < 4; i++)
      {
        vib_count[i] = 0;       // Reset vibration counter
        payload[i] = '0';         // Reset Payload
        prev_data[i] = curr_data[i];
      }
    }

    /************** Reset Values  *****************/
    /*                                            */
    for (int i = 0; i < 4; i++)
    {
      AccelMinX[i] = 0;
      AccelMaxX[i] = 0;
      AccelMinY[i] = 0;
      AccelMaxY[i] = 0;
      AccelMinZ[i] = 0;
      AccelMaxZ[i] = 0;
    }

  }

  /******************   Main Loop   ******************/
  /*                                                 */
  // Get the Accelerometer Readings
  tcaselect(0);
  adxl_1.readAccel(&x[0], &y[0], &z[0]);
  tcaselect(1);
  adxl_2.readAccel(&x[1], &y[1], &z[1]);
  tcaselect(2);
  adxl_3.readAccel(&x[2], &y[2], &z[2]);
  tcaselect(3);
  adxl_4.readAccel(&x[3], &y[3], &z[3]);

  for (int i = 0; i < 4; i++)
  {
    if (x[i] < AccelMinX[i]) AccelMinX[i] = x[i];
    if (x[i] > AccelMaxX[i]) AccelMaxX[i] = x[i];

    if (y[i] < AccelMinY[i]) AccelMinY[i] = y[i];
    if (y[i] > AccelMaxY[i]) AccelMaxY[i] = y[i];

    if (z[i] < AccelMinZ[i]) AccelMinZ[i] = z[i];
    if (z[i] > AccelMaxZ[i]) AccelMaxZ[i] = z[i];

    // Calculating Difference in Values for X, Y and Z
    diffX[i] = AccelMaxX[i] - AccelMinX[i];
    diffY[i] = AccelMaxY[i] - AccelMinY[i];
    diffZ[i] = AccelMaxZ[i] - AccelMinZ[i];
  }
}
