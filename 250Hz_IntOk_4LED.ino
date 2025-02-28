#include <Wire.h>
#include "Adafruit_AS726x.h"
#include <avr/interrupt.h>

#define INT_PIN 2  // Interrupt à la pin D2

Adafruit_AS726x ams;
bool rdy = false;
uint32_t last_time = 0;
uint16_t count = 0;
bool startTransmission = false;
int led1 = 8;
int led2 = 9;
int led3 = 10;
int led4 = 11;

volatile bool tickAcq = false;

#define BUF_SZ 200
uint16_t buffer[BUF_SZ] = {0};
uint16_t lastCount = 0;

void setupTimer1() {
  cli();
  TCCR1A = 0;
  TCCR1B = 0;
  TCCR1B |= (1 << WGM12);
  TCCR1B |= (1 << CS11) | (1 << CS10);
  OCR1A = 999;
  TIMSK1 |= (1 << OCIE1A);
  sei();
}

ISR(TIMER1_COMPA_vect) {
  tickAcq = true;
}

void setup() {
  Wire.begin();
  Serial.begin(460800);

  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(led3, OUTPUT);
  pinMode(led4, OUTPUT);
  
  digitalWrite(led1, HIGH);
  digitalWrite(led2, HIGH);
  digitalWrite(led3, HIGH);
  digitalWrite(led4, HIGH);

  if (!ams.begin()) {
    Serial.println("Erreur de connexion au capteur!");
    while (1);
  }

  ams.setIntegrationTime(2);
  ams.setConversionType(MODE_1);
  ams.setGain(GAIN_64X);

  pinMode(INT_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(INT_PIN), handleInterrupt, CHANGE);



  setupTimer1();

  while (!rdy) {
    rdy = ams.dataReady();
  }
  last_time = millis();

  Serial.println("initok");
}

void loop() {
  if (startTransmission && tickAcq && rdy) {
    tickAcq = false;

    if (count >= BUF_SZ) {
      lastCount = BUF_SZ;
      printBuffer();
      count = 0;
      last_time = millis();
    }
    
    uint8_t green_hgt = ams.virtualRead(AS7262_GREEN);
    uint8_t green_low = ams.virtualRead(AS7262_GREEN + 1);
    uint16_t green = (green_hgt << 8) | green_low;

    buffer[count] = green;
    count += 1;
  }
}

void handleInterrupt() {
  if (digitalRead(INT_PIN) == HIGH) {
    startTransmission = false;
    if (count > 0) {
      lastCount = count;
      printBuffer();
      count = 0;
    }
  } else {
    startTransmission = true;
  }
}

void printBuffer() {
  for (int i = 0; i < lastCount; i++) {
    Serial.print(buffer[i]);
    Serial.print(", ");
  }
  Serial.println("");
}
