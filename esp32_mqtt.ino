/*
  Author            : Mustafa ERGÜL
  Microcontroller   : ESP32-WROOM
  Screen            : ST7789
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <TFT_eSPI.h>
#include "bitmap.h"

TFT_eSPI tft = TFT_eSPI();              // Invoke library

// SSID/Password Variables assigned
const char* ssid = "Zyxel_CF61";
const char* password = "BLRTQG8RR3";

// Added MQTT Broker IP address
const char* mqtt_server = "192.168.1.41";

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
char dgr[20];
uint32_t Freq = 0;
String mess;
int measurement = 0;

void setup() {
  Serial.begin(115200);                // BaudRate = 115200  
  setup_wifi();                        //Wifi setup loaded
  client.setServer(mqtt_server, 1883); //Mqtt Broker ip address and port information is set
  client.setCallback(callback);        // callback set
  tft.begin();                         // ST7789 screen initialized
  tft.setSwapBytes(true);              // Changed byte order to pushImage()
  tft.fillScreen(TFT_BLACK);           // Screen cleared
}
void setup_wifi() {
  delay(10);
  // Wait for it to connect to WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  //Connected to WiFi network
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}
void callback(char* topic, byte* message, uint16_t length) {
  mess = "";
  for (uint16_t i = 0; i < length; i++) {
    mess += (char)message[i];                // Incoming message assigned to mess variable
  }
  //If a message is received in the CONTROL topic, if the mess content is 'play', the picture should be shown on the screen,
  //if it is 'stop', the screen should be cleared.
  //Changes the output state according to the message
  if (String(topic) == "CONTROL") {
    if(mess == "play"){
      tft.fillScreen(TFT_BLACK);
      tft.pushImage(0,0,240,240,mercy);
      Serial.println("Displaying the image");
    }
    else if(mess == "stop"){
      tft.fillScreen(TFT_BLACK);
      Serial.println("Image removed");
    }
 }
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP32")) {
      Serial.println("connected");
      // Subscribed to CONTROL
      client.subscribe("CONTROL");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  long now = millis();
  if (now - lastMsg > 5000) {
    lastMsg = now; 

    Freq = getCpuFrequencyMhz();     //CPU Frequency assigned to variable Freq
    sprintf(dgr,"%d",Freq);          //Freq variable converted to char variable
    client.publish("CPU",dgr);       //CPU frequency sent to CPU topic
    Freq = getXtalFrequencyMhz();    //XTAL Frequency assigned to variable Freq
    sprintf(dgr,"%d",Freq);          //Freq variable converted to char variable
    client.publish("XTAL",dgr);      //XTAL frequency sent to XTAL topic
    Freq = getApbFrequency();        //APB Frequency assigned to variable Freq
    sprintf(dgr,"%d",Freq);          //Freq variable converted to char variable
    client.publish("APB",dgr);       //APB frequency sent to XTAL topic
    measurement = hallRead();        //Hall measurement assigned to variable measurement
    sprintf(dgr,"%d",measurement);   //Freq variable converted to char variable
    client.publish("HALL",dgr);      //Measurement frequency sent to HALL topic
  }
}