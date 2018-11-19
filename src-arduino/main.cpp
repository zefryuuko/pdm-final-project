#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <Adafruit_MQTT.h>
#include <Adafruit_MQTT_Client.h>

// remember to delete ssid and password before pushing.
/* ----- Device Specific Setup ----- */
int RELAY_PINOUT = 4;
/* ----- WiFi & MQTT Setup ----- */
#define WLAN_SSID "WIFI SSID HERE"
#define WLAN_PASS "WIFI PASS HERE"
#define MQTT_ADDR "MQTT BROKER ADDRESS HERE"
#define MQTT_PORT 1883
WiFiClient client;
Adafruit_MQTT_Client mqtt(&client, MQTT_ADDR, MQTT_PORT);

/* ----- MQTT Feeds Setup ----- */
Adafruit_MQTT_Publish socket1Pub = Adafruit_MQTT_Publish(&mqtt, "socket1R");
Adafruit_MQTT_Subscribe socket1Sub = Adafruit_MQTT_Subscribe(&mqtt, "socket1");


/* ----- MQTT Functions ----- */
void MQTT_connect() {
  int8_t ret;

  // Stop if already connected.
  if (mqtt.connected()) {
    return;
  }

  Serial.print("Connecting to MQTT... ");

  uint8_t retries = 3;
  while ((ret = mqtt.connect()) != 0) { // connect will return 0 for connected
       Serial.println(mqtt.connectErrorString(ret));
       Serial.println("Retrying MQTT connection in 3 seconds...");
       mqtt.disconnect();
       delay(3000);  // wait 5 seconds
       retries--;
       if (retries == 0) {
         // basically die and wait for WDT to reset me
         while (1);
       }
  }
  Serial.println("MQTT Connected!");
}

void publishResponse(char* content) {
  Serial.println("Sending MsgAcceptedResponse");
  Serial.print("...");
  char* msgHeader = (char*)"MSGRCV socket1 ";
  char* message = (char*)malloc(1 + strlen(msgHeader)+ strlen(content));
  strcpy(message, msgHeader);
  strcat(message, content);
  if (! socket1Pub.publish(message)) {
    Serial.println(F("Failed to send MsgAcceptedResponse"));
  } else {
    Serial.println(F("MsgAcceptedResponse OK!"));
  }
}


/* ----- Main Setup ----- */
void setup() {
  pinMode(RELAY_PINOUT, OUTPUT);

  Serial.begin(9600);
  Serial.print("Connecting to "); Serial.println(WLAN_SSID);

  WiFi.begin(WLAN_SSID, WLAN_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi connected");
  Serial.println("IP address: "); Serial.println(WiFi.localIP());

  // Setup MQTT subscription for onoff feed.
  mqtt.subscribe(&socket1Sub);

}

/* ----- Main Loop ----- */
void loop() {
  MQTT_connect();
  Adafruit_MQTT_Subscribe *subscription;

  while ((subscription = mqtt.readSubscription(5000))) {
    if (subscription == &socket1Sub) {
      int socket1SubVal = atoi((char*)socket1Sub.lastread);
      Serial.print(F("Got: ")); Serial.println(socket1SubVal);
      if (socket1SubVal == 1) {
        Serial.println("Setting pin 4 to ON");
        digitalWrite(RELAY_PINOUT, HIGH);
      } else if (socket1SubVal == 0) {
        Serial.println("Setting pin 4 to OFF");
        digitalWrite(RELAY_PINOUT, LOW);
      } else {
        Serial.println("I did nothing");
      }
      char subVal[10];
      itoa(socket1SubVal, subVal, 10);
      publishResponse((char*)subVal);
    }
  }

}
