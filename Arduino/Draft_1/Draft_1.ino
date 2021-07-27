#include <Time.h>
#include "EspMQTTClient.h"

EspMQTTClient client(
  "A12",
  "00000000",
  "broker.emqx.io",  // MQTT Broker server ip
  "",   // Can be omitted if not needed
  "",   // Can be omitted if not needed
  "laundrobot_pub"      // Client name that uniquely identify your device
);
int inputs[4] = {33, 32, 35, 34}; //Input Pins
char payload[3];
char curr_state[5];
void onConnectionEstablished() {
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  // CHECK FOR CURRENT STATE
  for (int i = 0; i < 4; i++)
  {
    if (analogRead(inputs[i]) > 4000)
    {
      curr_state[i] = '1';
    }
    else
      curr_state[i] = '0';
  }

  Serial.print("INITIAL STATE: "); Serial.print(curr_state); Serial.println();
}

void loop() {
  // put your main code here, to run repeatedly:
  client.loop();

  for (int i = 0; i < 4; i++)
  {
    if (analogRead(inputs[i]) > 4000)
    {
      if (curr_state[i] == '0')
      {
        payload[0] = i + '1';
        payload[1] = '1';

        Serial.println(payload);
        client.publish("laundrobot", payload);
      }
      curr_state[i] = '1';
    }
    else
    {
      if (curr_state[i] == '1')
      {
        payload[0] = i + '1';
        payload[1] = '0';

        Serial.println(payload);
        client.publish("laundrobot", payload);
      }
      curr_state[i] = '0';
    }

    delay(100);
  }
}
