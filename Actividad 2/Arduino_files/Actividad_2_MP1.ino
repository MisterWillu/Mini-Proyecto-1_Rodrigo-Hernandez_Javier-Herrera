#include <DHT.h>

#define DHTPIN 4        // Pin digital al que está conectado el sensor
#define DHTTYPE DHT11   // Tipo de sensor DHT utilizado (DHT11 en este caso)

const int ledB = 9;
const int ledG = 10;
const int ledR = 11;

const int botonPin = 2;
const int pinTiltSwitch = 3; // Pin digital al que está conectado el sensor KY-017
const int pinFotorresistor = 7; // Pin digital al que está conectado el sensor KY-018

int oldVal;
int oldVal2;
int oldVal3;

int alive_cells;  // Cantidad de células vivas recibidas desde Python
bool reiniciar = false;

DHT dht(DHTPIN, DHTTYPE);

unsigned long previousMillis = 0;   // Almacena el tiempo del último envío
const long interval = 3000;         // Intervalo de tiempo entre envíos (en milisegundos)

void setup() {
  Serial.begin(9600);
  dht.begin();        // Inicializa el sensor DHT

  pinMode(ledB, OUTPUT);
  pinMode(ledG, OUTPUT);
  pinMode(ledR, OUTPUT);
  pinMode(botonPin, INPUT_PULLUP);
  pinMode(pinTiltSwitch, INPUT_PULLUP); // Establece el pin como entrada con resistencia pull-up
  pinMode(pinFotorresistor, INPUT_PULLUP); // Establece el pin como entrada

  oldVal = digitalRead(botonPin);
  oldVal2 = digitalRead(pinTiltSwitch);
  oldVal3 = digitalRead(pinFotorresistor);
}

void loop() {
  int val = digitalRead(botonPin);
  int val2 = digitalRead(pinTiltSwitch);
  int val3 = digitalRead(pinFotorresistor);

  if (val2==LOW && oldVal2==HIGH) {
  // El botón fue presionado
  Serial.println("b-1");
  }
  else if (val2==HIGH && oldVal2==LOW)
  {
  Serial.println("b-0");
  }
  else
  {
  // Otro caso
  }
  oldVal2 = val2;
  delay(10);

  if (val3==LOW && oldVal3==HIGH) {
  // El botón fue presionado
  Serial.println("a-1");
  }
  else if (val3==HIGH && oldVal3==LOW)
  {
  Serial.println("a-0");
  }
  else
  {
  // Otro caso
  }
  oldVal3 = val3;
  delay(10);


  if (val==LOW && oldVal==HIGH) {
  // El botón fue presionado
  Serial.println("Reiniciar"); // Enviar mensaje de reinicio a Python
  }
  else if (val==HIGH && oldVal==LOW)
  {
  reiniciar = false; // Restablecer la bandera de reinicio
  }
  else
  {
  // Otro caso
  }
  oldVal = val;
  delay(10);


  if (reiniciar) {
    Serial.println("Reiniciar"); // Enviar mensaje de reinicio a Python
    reiniciar = false; // Restablecer la bandera de reinicio
  }

  if (Serial.available() > 0) {
    // Leer el número de células vivas desde Python
    alive_cells = Serial.read();

    if (alive_cells == 'E') {
      digitalWrite(ledB, HIGH);
      digitalWrite(ledG, LOW);
      digitalWrite(ledR, LOW);
    }
    if (alive_cells == 'S') {
      digitalWrite(ledB, LOW);
      digitalWrite(ledG, HIGH);
      digitalWrite(ledR, LOW);
    }
    if (alive_cells == 'A') {
      digitalWrite(ledB, LOW);
      digitalWrite(ledG, LOW);
      digitalWrite(ledR, HIGH);
    }
  }

  unsigned long currentMillis = millis();  // Obtiene el tiempo actual
  
  // Realiza otras tareas en el loop principal
  
  // Verifica si ha pasado el intervalo de tiempo para enviar la temperatura
  if (currentMillis - previousMillis >= interval) {
    // Actualiza el tiempo del último envío
    previousMillis = currentMillis;
    
    // Lee la temperatura del sensor DHT11
    float temperatura = dht.readTemperature();
    
    // Verifica si la lectura del sensor fue exitosa
    if (!isnan(temperatura)) {
      // Imprime la temperatura en el puerto serie
      Serial.print("t-");
      Serial.println(temperatura);
    } else {
      Serial.println("Error al leer el sensor DHT!");
    }
  }
}