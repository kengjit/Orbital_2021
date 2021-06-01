#include <Arduino.h>
#include <Wire.h>
#include <dummy.h> //for esp32

#define SPEED 10000
#define SDA1 21
#define SCL1 22

#define SDA2 19
#define SCL2 23

TwoWire I2COne, I2CTwo; // create variables

void setup() {
  Serial.begin(115200);

  I2COne = TwoWire(0); //initialize using the first i2c peripheral
  I2CTwo = TwoWire(1); // initialize using the second i2c peripheral

  I2COne.begin(SDA1, SCL1, SPEED); // you have to select which pins and speed
  I2CTwo.begin(SDA2, SCL2, SPEED);
}
void loop() {


}
