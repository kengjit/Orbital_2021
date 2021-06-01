// Import required libraries
#include <AWS_IOT.h>
#include "WiFi.h"
#include <Time.h>
#include <TimeLib.h>
#include <SparkFun_ADXL345.h>

/*********** COMMUNICATION SELECTION ***********/
/*    Comment Out The One You Are Not Using    */
ADXL345 adxl = ADXL345();             // Use when you need I2C

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

time_t t;
/************** DEFINED VARIABLES **************/
/*                                             */
#define ThresholdX 20
#define ThresholdY 80
#define ThresholdZ 280

/************** FUNCTIONS **********************/
/*                                             */
bool is_vibrating(int diffX, int diffY, int diffZ)
{
  return (diffX > ThresholdX && diffY > ThresholdY && diffZ > ThresholdZ);
}

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
    if (is_vibrating(diffX, diffY, diffZ))
    {
      vib_count++;
    }

    // Debugging
    Serial.print("["); Serial.print(minute(t)); Serial.print(":"); Serial.print(second(t)); Serial.print("] ");
    Serial.print(diffX); Serial.print("  "); Serial.print(diffY); Serial.print("  "); Serial.print(diffZ); Serial.print("  VC:"); Serial.print(vib_count); Serial.print("  QC:"); Serial.print(quadrant_count);
    Serial.println();

    /*********  Triggers every 1 minute  *************/
    /*                                               */
    if (quadrant_count == 4)
    {
      if (vib_count == 4)
      {
        sprintf(payload, "1"); // Create the payload for publishing
      }
      else
      {
        sprintf(payload, "0"); // Create the payload for publishing
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
      vib_count = 0;       // Reset vibration counter
    }

    /************** Reset Values  *****************/
    /*                                            */
    AccelMinX = 0;
    AccelMaxX = 0;
    AccelMinY = 0;
    AccelMaxY = 0;
    AccelMinZ = 0;
    AccelMaxZ = 0;
  }

  /******************   Main Loop   ******************/
  /*                                                 */
  // Get the Accelerometer Readings
  adxl.readAccel(&x, &y, &z);         // Read the accelerometer values and store them in variables declared above x,y,z

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
