#include "DHT.h"

#define DHTPIN 2      // Use the pin number you've connected to the Data pin of DHT22
#define DHTTYPE DHT21 // DHT 21 (AM2302)

DHT dht(DHTPIN, DHTTYPE);

int light;
String hello;
float temperature, humidity;
int thresold = 700; // for ldr
int sensor_pin_fc28 = A1; 
int sensor_pin_fc37 = A0; 
int fc_28;

// Add new variables for the pump control
int pumpPin = 4;  // Change to the pin you connect the relay module control pin to
int moistureThreshold = 15;  // Adjust this threshold based on your soil moisture readings

const int sensorMin = 0;     // sensor minimum for fc37
const int sensorMax = 1024;  // sensor maximum for fc37

void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(6, OUTPUT);  // Set pumpPin as an output
  pinMode(7, OUTPUT);
}

void loop() {
  light = analogRead(A2);
  if(light < thresold)
  {
    digitalWrite(7, HIGH);
  }
  else
  {
    digitalWrite(7, LOW);
  }
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  fc_28= analogRead(sensor_pin_fc28);
  int moisturePercentage = 100 - map(fc_28, 0, 1023, 0, 100);

  // Control the pump based on soil moisture
  if (moisturePercentage > moistureThreshold) {
    digitalWrite(6, LOW);  // Turn on the pump
  } else {
    digitalWrite(6, HIGH);   // Turn off the pump
  }

  int rain = analogRead(sensor_pin_fc37);

  hello = String(light) + "," + String(temperature) + "," + String(humidity) + "," + String(moisturePercentage) + "," + String(rain);
  char helloCharArray[hello.length() + 1];
  hello.toCharArray(helloCharArray, hello.length() + 1);

  for (int i = 0; i < hello.length(); i++) {
    Serial.write(helloCharArray[i]);
  }
  Serial.write("\n");
  Serial.println(hello);
  delay(2000);
}
