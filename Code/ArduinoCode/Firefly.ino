// Upload libraries
#include <Wire.h>
#include <BH1750.h>

// Declare luminosity meter
BH1750 lightMeter;

// Declare variables
const int ledPin = 11;
const int capacitorPin = 12;
const int kickPin = 13;

int capacitorState = LOW;
int kickState = LOW;

float luxMeasurements[20]; 
int capacitorCharge;

const long kickLength = 2;
const long refractoryPeriod = 100;
long countKick = 0;
long countRefractory = 0;

void setup(){
  Serial.begin(9600);
  // Initialize the I2C bus (BH1750 library doesn't do this automatically)
  Wire.begin();

  // Initialize luminosity meter
  lightMeter.begin();

  // Set initial values
  pinMode(ledPin, OUTPUT);
  pinMode(capacitorPin, OUTPUT);
  pinMode(kickPin, OUTPUT);
  digitalWrite(ledPin, capacitorState);
  digitalWrite(capacitorPin, capacitorState);
  digitalWrite(kickPin, kickState);

  for (int i = 0; i <= 19; i++) { 
    luxMeasurements[i]=0.0;
  }
}

void loop() {
  // Update counters
  countKick = countKick+1;
  countRefractory = countRefractory+1;

  // Measure capacitor charge
  capacitorCharge = analogRead(A0);

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

  // Decide if capacitor charging/unchargin state flips
  if (capacitorCharge <= 300 || capacitorCharge >= 723) {
    capacitorState = !capacitorState;
    digitalWrite(ledPin,capacitorState);
    digitalWrite(capacitorPin, capacitorState);
  }
  else {
    // Decide if system receives a kick due to a nearby light turning on
    if (countRefractory>=refractoryPeriod && lux1>1.2*lux0) {
      countKick = 0;
      countRefractory = 0;
      kickState = HIGH;
      digitalWrite(kickPin, kickState);
      //Serial.println("1");
    }

  }

  // Stop kick
  if (kickState==HIGH && countKick>=kickLength){
    kickState = LOW;
    digitalWrite(kickPin, kickState);
  }

  delay(1);
}
