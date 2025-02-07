// Upload libraries
#include <Wire.h>
#include <BH1750.h>

// Declare luminosity meter
BH1750 lightMeter;


float luxMeasurements[20]; 
const int ledPin = 13;
int ledState = LOW;
const long refractoryPeriod = 100;
long countRefractory = 0;
const long onDuration = 300;
long countOn = 0;


void setup(){
  Serial.begin(9600);
  // Initialize the I2C bus (BH1750 library doesn't do this automatically)
  Wire.begin();
  // Initialize luminosity meter
  lightMeter.begin();

  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, ledState);
  for (int i = 0; i <= 19; i++) { 
    luxMeasurements[i]=0.0;
  }

}

void loop() {
  countRefractory = countRefractory+1;
  countOn = countOn + 1;

  // Update stack of luminosity measurements with last measure
  for (int i = 0; i <= 18; i++) {
    luxMeasurements[i]=luxMeasurements[i+1];
  }
  luxMeasurements[19] = lightMeter.readLightLevel();

  // Compute averages
  float lux0 = 0.0;
  float lux1 = 0.0;
  
  for (int i = 0; i <= 9; i++) {
    lux0 = lux0 + luxMeasurements[i];
    lux1 = lux1 + luxMeasurements[i+10];
  }

  if (countRefractory>=refractoryPeriod && lux1>1.2*lux0){
    countRefractory = 0;
    countOn = 0;
    ledState = HIGH;
    digitalWrite(ledPin, ledState);
  }

    // Switch off
  if (ledState==HIGH && countOn>=onDuration){
    ledState = LOW;
    digitalWrite(ledPin, ledState);
  }

  delay(1);
}
