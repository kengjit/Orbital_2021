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

time_t t;
/************** DEFINED VARIABLES **************/
/*                                             */
#define ThresholdX 10
#define ThresholdY 70
#define ThresholdZ 240

/************** FUNCTIONS **************/
/*                                             */
bool is_vibrating(int diffX, int diffY, int diffZ)
{
  return (diffX > ThresholdX && diffY > ThresholdY && diffZ > ThresholdZ);
}

/******************** SETUP ********************/
/*          Configure ADXL345 Settings         */
void setup()
{
  Serial.begin(115200);                 // Start the serial terminal
  Serial.println("SparkFun ADXL345 Accelerometer Breakout Calibration");
  Serial.println();

  adxl.powerOn();                     // Power on the ADXL345

  adxl.setRangeSetting(2);           // Give the range settings
  // Accepted values are 2g, 4g, 8g or 16g
  // Higher Values = Wider Measurement Range
  // Lower Values = Greater Sensitivity
}

/****************** MAIN CODE ******************/
/*  Accelerometer Readings and Min/Max Values  */
void loop()
{
  int x, y, z;                        // init variables hold results
  int count = 0; // Number of Samples taken
  // Reset Values
  AccelMinX = 0;
  AccelMaxX = 0;
  AccelMinY = 0;
  AccelMaxY = 0;
  AccelMinZ = 0;
  AccelMaxZ = 0;
  while (count < 10000)
  {
    // Get the Accelerometer Readings
    adxl.readAccel(&x, &y, &z);         // Read the accelerometer values and store them in variables declared above x,y,z

    if (x < AccelMinX) AccelMinX = x;
    if (x > AccelMaxX) AccelMaxX = x;

    if (y < AccelMinY) AccelMinY = y;
    if (y > AccelMaxY) AccelMaxY = y;

    if (z < AccelMinZ) AccelMinZ = z;
    if (z > AccelMaxZ) AccelMaxZ = z;

    count++;
  }

  // Measure and Print Current time
  t = now();
  Serial.print("[");
  Serial.print(hour(t));
  Serial.print(":");
  Serial.print(minute(t));
  Serial.print(":");
  Serial.print(second(t));
  Serial.print("]  ");

  // Calculating Difference in Values for X, Y and Z
  diffX = AccelMaxX - AccelMinX;
  diffY = AccelMaxY - AccelMinY;
  diffZ = AccelMaxZ - AccelMinZ;

  if (is_vibrating(diffX, diffY, diffZ))
  {
    Serial.print("VIBRATING");
    Serial.println();
  }
  else
  {
    Serial.println("STILL");
  }


    Serial.print("New Calibrated Values: "); Serial.print(diffX); Serial.print("  "); Serial.print(diffY); Serial.print("  "); Serial.print(diffZ);
    Serial.println();

}
