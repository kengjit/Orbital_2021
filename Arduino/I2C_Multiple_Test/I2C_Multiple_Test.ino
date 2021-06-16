#include <SparkFun_ADXL345.h>
#include <Arduino.h>
#include <Wire.h>
#include <dummy.h> //for esp32

ADXL345 adxl_1 = ADXL345();
ADXL345 adxl_2 = ADXL345();
ADXL345 adxl_3 = ADXL345();
ADXL345 adxl_4 = ADXL345();


#define TCAADDR 0x70
void tcaselect (uint8_t i) {
  if (i > 7) return;

  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
}

void setup() {
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
}

void loop() {
  tcaselect(0);
  int x_1, y_1, z_1;       // init variables hold results
  adxl_1.readAccel(&x_1, &y_1, &z_1);         // Read the accelerometer values and store them in variables declared above x,y,z
  Serial.println("**************************************************");
  Serial.println("ADXL 1: ");
  Serial.print(x_1); Serial.print("  "); Serial.print(y_1); Serial.print("  "); Serial.print(z_1);
  Serial.println();

  tcaselect(1);
  int x_2, y_2, z_2;       // init variables hold results
  adxl_2.readAccel(&x_2, &y_2, &z_2);         // Read the accelerometer values and store them in variables declared above x,y,z
  Serial.println("ADXL 2:  ");
  Serial.print(x_2); Serial.print("  "); Serial.print(y_2); Serial.print("  "); Serial.print(z_2);
  Serial.println();

  tcaselect(2);
  int x_3, y_3, z_3;       // init variables hold results
  adxl_3.readAccel(&x_3, &y_3, &z_3);         // Read the accelerometer values and store them in variables declared above x,y,z
  Serial.println("ADXL 3:  ");
  Serial.print(x_3); Serial.print("  "); Serial.print(y_3); Serial.print("  "); Serial.print(z_3);
  Serial.println();

  tcaselect(3);
  int x_4, y_4, z_4;       // init variables hold results
  adxl_4.readAccel(&x_4, &y_4, &z_4);         // Read the accelerometer values and store them in variables declared above x,y,z
  Serial.println("ADXL 4:  ");
  Serial.print(x_4); Serial.print("  "); Serial.print(y_4); Serial.print("  "); Serial.print(z_4);
  Serial.println();
  Serial.println("**************************************************");
}
