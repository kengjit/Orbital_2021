// Import required libraries
#include <AWS_IOT.h>
#include "WiFi.h"
#include <Time.h>
#include <TimeLib.h>
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

time_t t;

/****************** THRESHOLD VALUES ******************/
/*                                                    */
int ThresholdX[4] = {20, 20, 20, 20};
int ThresholdY[4] = {40, 40, 40, 40};
int ThresholdZ[4] = {240, 240, 240, 240};

//// Sensor 1
//ThresholdX[0] = 20;
//ThresholdY[0] = 40;
//ThresholdZ[0] = 240;
//// Sensor 2
//ThresholdX[1] = 20;
//ThresholdY[1] = 40;
//ThresholdZ[1] = 240;
//// Sensor 3
//ThresholdX[2] = 20;
//ThresholdY[2] = 40;
//ThresholdZ[2] = 240;
//// Sensor 4
//ThresholdX[3] = 20;
//ThresholdY[3] = 40;
//ThresholdZ[3] = 240;

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
  return (diffX > ThresholdX[sensor] && diffY > ThresholdY[sensor] && diffZ > ThresholdZ[sensor]);
}

/************** NETWORK + AWS SETUP **************/
/*                                             */
AWS_IOT hornbill;   // AWS_IOT instance
const char* ssid = "dlink-D8EA"; //Replace with your WiFi Name
const char* password = "bootl72707"; // Replace with your WiFi Password
char HOST_ADDRESS[] = "ah0mtuita99jn-ats.iot.us-east-1.amazonaws.com"; //Replace with your AWS Custom endpoint Address

char CLIENT_ID[] = "ADXL345_DATA";
char TOPIC_NAME[] = "ESP32/ADXL345_DATA";
int status = WL_IDLE_STATUS;
char payload[512];


void setup() {
  // Serial port for debugging purposes
  Serial.begin(115200);

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
  int x[4], y[4], z[4];       // init variables hold results
  t = now();         // init Time
  static uint32_t previousTime = 0;
  uint32_t currentTime = millis();

  /*********  Triggers every 15 secs  *************/
  /*                                              */
  if ( currentTime - previousTime >= 15000)
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
    Serial.print("["); Serial.print(minute(t)); Serial.print(":"); Serial.print(second(t)); Serial.print("] ");
    Serial.println();
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
          //          sprintf(payload, "1"); // Create the payload for publishing
          payload[i] = '1';
        }
        else
        {
          //          sprintf(payload, "0"); // Create the payload for publishing
          payload[i] = '0';
        }
      }


      /*************** Upload to AWS ***************/
      /*                                           */
      if (hornbill.publish(TOPIC_NAME, payload) == 0) // Publish the message
      {
        Serial.print("Publish Message:");
        Serial.println(payload);
      }
      else
      {
        Serial.println("Publish failed");
      }
      quadrant_count = 0;  // Reset minute counter
      for (int i = 0; i < 4; i++)
      {
        vib_count[i] = 0;       // Reset vibration counter
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
