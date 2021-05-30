#include <SparkFun_ADXL345.h>
/*********** COMMUNICATION SELECTION ***********/
/*    Comment Out The One You Are Not Using    */
ADXL345 adxl = ADXL345();             // Use when you need I2C

/****************** VARIABLES ******************/
/*                                             */

#define SAMPLES_TO_TAKE 3

int AccelMinX = 0;
int AccelMaxX = 0;
int AccelMinY = 0;
int AccelMaxY = 0;
int AccelMinZ = 0;
int AccelMaxZ = 0;

int diffX = 0;
int diffY = 0;
int diffZ = 0;

int samples_taken = 0;
int totalX = 0;
int totalY = 0;
int totalZ = 0;

bool shown_average = false;

/******************** SETUP ********************/
/*          Configure ADXL345 Settings         */

void setup()
{
  Serial.begin(115200);                 // Start the serial terminal
  Serial.println("Taking Samples...");
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
  if (samples_taken < SAMPLES_TO_TAKE)
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

    // Calculating Difference in Values for X, Y and Z
    diffX = AccelMaxX - AccelMinX;
    diffY = AccelMaxY - AccelMinY;
    diffZ = AccelMaxZ - AccelMinZ;

    totalX += diffX;
    totalY += diffY;
    totalZ += diffZ;


    Serial.print("[Sample "); Serial.print(samples_taken + 1); Serial.print("] ");
    Serial.print("XYZ Values: "); Serial.print(diffX); Serial.print("  "); Serial.print(diffY); Serial.print("  "); Serial.print(diffZ);
    Serial.println();

    samples_taken++;
  }
  else if (!shown_average) {
    Serial.print("Average Values: "); Serial.print(totalX / SAMPLES_TO_TAKE); Serial.print("  "); Serial.print(totalY / SAMPLES_TO_TAKE); Serial.print("  "); Serial.print(totalZ / SAMPLES_TO_TAKE);
    Serial.println();

    shown_average = true;
  }
  else {
  }
}
