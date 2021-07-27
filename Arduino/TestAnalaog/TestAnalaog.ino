
#include <Time.h>

int inputs[4] = {33, 32, 35, 34};

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(10);
  for (int i = 0; i < 4; i++)
  {
    if (analogRead(inputs[i]) > 4000)
    {
      Serial.print(i);
      Serial.print(": ");
      Serial.print("CONNECT");
      Serial.println();
    }
    else
    {
      Serial.print(i);
      Serial.print(": ");
      Serial.println("DISCONNECT");
      Serial.println();
    }
  }
  Serial.println();
}
