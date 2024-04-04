#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <Hash.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>

// Replace with your network credentials
const char* ssid = "realme X7 Max";
const char* password = "rickysaha";

int ldrPin = 0; // LDR sensor connected to GPIO4
int ldrValue = 0;     // Variable to store LDR sensor reading


// current temperature & humidity, updated in loop()
float t = 0.0;
float h = 0.0;
float temperature=0.0, humidity=0.0;

int thresold = 170; // for ldr
int sensor_pin_fc28 = 2; 
int sensor_pin_fc37 = 1; 
int fc_28;
int fc_37;

String inputString = "";

// Create AsyncWebServer object on port 80
AsyncWebServer server(80);

// Generally, you should use "unsigned long" for variables that hold time
// The value will quickly become too large for an int to store
unsigned long previousMillis = 0;    // will store last time DHT was updated

// Updates DHT readings every 10 seconds
const long interval = 5000;  

// Replaces placeholder with DHT values
// String processor(const String& var){
//   if(var == "TEMPERATURE"){
//     return String(t);
//   }
//   else if(var == "HUMIDITY"){
//     return String(h);
//   }
//   else if(var == "LDR"){
//     return String(ldrValue);
//   }
//   else if(var == "SOIL"){
//     return String(fc_28);
//   }
//   else if(var == "RAIN"){
//     return String(fc_37);
//   }
//   return String();
// }

int splitString(String input, char delimiter, String output[]) {
  int index = 0;
  int start = 0;
  int end = input.indexOf(delimiter);
  while (end >= 0) {
    output[index] = input.substring(start, end);
    index++;
    start = end + 1;
    end = input.indexOf(delimiter, start);
  }
  // Add the last part of the input (after the last delimiter)
  output[index] = input.substring(start);
  return index + 1; // Return the number of values found
}

void setup(){
  // Serial port for debugging purposes
  Serial.begin(115200);
  
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println(".");
  }
  Serial.println("Connected to WiFi!");

  // Print ESP8266 Local IP Address
  Serial.println(WiFi.localIP());

  // Route for root / web page
  // server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
  //   request->send_P(200, "text/html", index_html, processor);
  // });
  server.on("/temperature", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send_P(200, "text/plain", String(t).c_str());
  });
  server.on("/humidity", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send_P(200, "text/plain", String(h).c_str());
  });
  server.on("/ldr", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send_P(200, "text/plain", String(ldrValue).c_str());
  });
  server.on("/soil-mois", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send_P(200, "text/plain", String(fc_28).c_str());
  });
  server.on("/rain", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send_P(200, "text/plain", String(fc_37).c_str());
  });
  // Start server
  server.begin();
}
 
void loop(){ 
  while (Serial.available() > 0) {
    char incomingChar = Serial.read(); // Read the incoming character
    inputString += incomingChar; // Append it to the inputString
    if (incomingChar == '\n') { // If a newline character is received
      inputString.trim(); // Remove any leading/trailing whitespace

      // Split the inputString into individual integer values based on a delimiter (e.g., comma)
      String values[5]; // Assuming a maximum of 10 values (adjust as needed)
      int numValues = splitString(inputString, ',', values);

      ldrValue = values[0].toInt();
      temperature = values[1].toFloat();
      humidity = values[2].toFloat();
      fc_28 = values[3].toInt();
      fc_37 = values[4].toInt();

      unsigned long currentMillis = millis();
      if (currentMillis - previousMillis >= interval) {
        // save the last time you updated the DHT values
        previousMillis = currentMillis;
        
        t = temperature;
        Serial.println(t);
        
        h = humidity;
        Serial.println(h);

        Serial.println(ldrValue);
        Serial.println(fc_28);
        Serial.println(fc_37);
      }
      inputString = "";
    }
  } 
}

