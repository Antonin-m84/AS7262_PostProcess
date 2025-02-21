#include <Wire.h>
#include "Adafruit_AS726x.h"
#include <avr/interrupt.h>

#define INT_PIN 2  // Interrupt à la pin D2

Adafruit_AS726x ams;
bool rdy = false; // 
uint32_t last_time = 0;
uint16_t count = 0;
bool startTransmission = false;
int led1 = 10; // Broche pour la LED verte
int led2 = 11;

volatile bool tickAcq = false;

#define BUF_SZ 200
uint16_t buffer[BUF_SZ] = {0};
uint16_t lastCount = 0; // Nombre de valeurs du dernier buffer affiché


void setupTimer1() {
  cli(); // Disable interrupts
  TCCR1A = 0; // Normal mode
  TCCR1B = 0; 
  TCCR1B |= (1 << WGM12); // CTC mode
  TCCR1B |= (1 << CS11) | (1 << CS10); // Prescaler 64
  // OCR1A = 1249; // 16MHz / (64 * 1250) = 200Hz (5ms)
  OCR1A = 999; // 16MHz / (64 * 1000) = 250Hz (4ms) à l'oscillo = 249,9Hz
  // OCR1A = 832; // 16MHz / (64 * 832) = 300Hz (3.3ms)
  TIMSK1 |= (1 << OCIE1A); // Enable Timer1 Compare Match A Interrupt

  sei(); // Enable interrupts
}

ISR(TIMER1_COMPA_vect) {
  // digitalWrite(6, HIGH); // Set pin digital 6 to 1
  tickAcq = true;
  // digitalWrite(6, LOW);  // Set pin digital 6 to 0
}



void setup() {
  Wire.begin();
  Serial.begin(460800);

  if (!ams.begin()) {
    Serial.println("Erreur de connexion au capteur!");
    while (1);
  }

  ams.setIntegrationTime(3);  // Temps d'intégration minimal (2.8ms)
  ams.setConversionType(MODE_1); // Mode 1 : G, Y, O, R en continu
  ams.setGain(GAIN_64X); // Gain maximal

  pinMode(INT_PIN, INPUT_PULLUP); // Met D2 en entrée avec une résistance pull-up 10K
  attachInterrupt(digitalPinToInterrupt(INT_PIN), handleInterrupt, CHANGE);

  // Allume une led, a dupliquer pour 2, 4 ...
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  analogWrite(led1, 0); // Allume la couleur (0 = max pour une anode commune)
  analogWrite(led2, 0);

  setupTimer1(); // Timer a 200-300Hz selon OCR1A

  while (!rdy) {
    rdy = ams.dataReady();
  }
  last_time = millis();
  

  Serial.println("initok");
}



void loop() { //StartTransmission = signal début rec tapis / tickacq = tick a 250Hz pour l'acquisition / rdy = data ready to read
  if (startTransmission && tickAcq && rdy) {
    tickAcq = false;

    if (count >= BUF_SZ) { // Si le compteur de taille du buffer atteint la taille max (BUF_SZ) alors...
      lastCount = BUF_SZ; // Enregistre la taille du buffer complet
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
  if (digitalRead(INT_PIN) == LOW) {
    startTransmission = false;

    if (count > 0) { // cas ou buffer final
      lastCount = count; // Enregistre la taille du dernier buffer incomplet
      printBuffer(); // Print le dernier buffer incomplet
      count = 0;
    }
  } else { // cas typique pendant transmission
    startTransmission = true;
  }
}


void printBuffer() {

  /* Print Frequence
  // uint32_t delta = millis() - last_time;
  // if (delta > 0) {
  //   float frequency = (lastCount * 1000.0) / delta; // Calcul correct avec la vraie taille du buffer
  //   Serial.print(frequency);
  //   Serial.println(" Hz");
  // }
  */

  // Serial.println("Greens :");
  for (int i = 0; i < lastCount; i++) {
    Serial.print(buffer[i]);
    Serial.print(", ");
  }
  Serial.println("");
}