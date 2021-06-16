#include "EspMQTTClient.h"

EspMQTTClient client(
  "dlink-D8EA",
  "bootl72707",
  "broker.emqx.io",  // MQTT Broker server ip
  "",   // Can be omitted if not needed
  "",   // Can be omitted if not needed
  "laundrobot_pub"      // Client name that uniquely identify your device
);

void setup() {
  Serial.begin(115200);
  // Optionnal functionnalities of EspMQTTClient :
  client.enableDebuggingMessages(); // Enable debugging messages sent to serial output
  client.enableHTTPWebUpdater(); // Enable the web updater. User and password default to values of MQTTUsername and MQTTPassword. These can be overrited with enableHTTPWebUpdater("user", "password").
  client.enableLastWillMessage("laundrobot", "I am going offline");  // You can activate the retain flag by setting the third parameter to true

}

void onConnectionEstablished() {

  client.subscribe("laundrobot", [] (const String & payload)  {
    Serial.println(payload);
  });

  client.publish("laundrobot", "This is a message");
}

void loop() {
  client.loop();
}
