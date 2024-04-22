const int ledPins[] = {13, 12, 8}; // Pines de los LED (topos)
const int buttonPins[] = {10, 11, 9}; // Pines de los botones (martillos)
const int buzzerPin = 5; // Pin del buzzer
const int numLEDs = 3;
const int numButtons = 3;
int activeMole; // Mole activo (LED) en la secuencia actual
int score; // Puntaje inicial
unsigned long moleDisplayTime; // Tiempo de visualización del topo (en milisegundos) ajustado según el nivel
unsigned long baseMoleDisplayTime[] = {1500, 1000, 500}; // Tiempos de visualización del topo base para cada nivel de dificultad
enum Difficulty { FACIL, NORMAL, DIFICIL }; // Enumeración para los niveles de dificultad
Difficulty currentDifficulty; // Nivel de dificultad inicial
bool printedDifficulty = false; // Bandera para controlar si se ha impreso la dificultad al inicio
unsigned long startTime; // Tiempo de inicio del juego
bool level2Printed = false; // Bandera para controlar si se ha impreso "Nivel 2"
bool level3Printed = false; // Bandera para controlar si se ha impreso "Nivel 3"

void setup() {
  Serial.begin(9600); // Iniciar comunicación serial
  while (!Serial);

  pinMode(buzzerPin, OUTPUT); // Configurar el pin del buzzer como salida

  for (int i = 0; i < numLEDs; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }
  
  for (int i = 0; i < numButtons; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
  }
}

void loop() {
  waitForDifficulty();
  printedDifficulty = false; // Reiniciar la bandera de impresión de la dificultad al inicio
  startTime = millis(); // Iniciar el contador de tiempo de juego
  while (true) { // Bucle principal del juego
    displayScore();
    delay(1000); // Tiempo para prepararse antes de mostrar un nuevo topo
    activeMole = random(numLEDs); // Escoge un nuevo topo aleatorio
    digitalWrite(ledPins[activeMole], HIGH); // Enciende el LED correspondiente al topo
    setDifficulty(currentDifficulty); // Ajusta el tiempo de visualización del topo y el puntaje según el nivel de dificultad
    delay(moleDisplayTime); // Tiempo que el topo permanece encendido
    digitalWrite(ledPins[activeMole], LOW); // Apaga el LED
    int playerHit = waitForInput(); // Espera que el jugador golpee un topo
    if (playerHit == activeMole) {
      score += 10; // Incrementa el puntaje si el jugador golpea el topo correcto
      tone(buzzerPin, 1000, 100); // Sonar el buzzer (tono de 1000 Hz por 100 ms) cuando golpea bien un topo
    } else {
      score -= 5; // Reduce el puntaje en 5 si el jugador golpea el topo incorrecto
      if (score < 0) {
        score = 0; // Asegura que el puntaje no sea negativo
      }
      tone(buzzerPin, 500, 200); // Sonar el buzzer (tono de 500 Hz por 200 ms) cuando golpea mal un topo
    }

    // Verificar si el puntaje es igual o menor que cero
    if (score <= 0) {
      // Detener el juego
      tone(buzzerPin, 150, 1000); // Sonar un tono largo para indicar que el juego ha terminado
      while (true) {} // Bucle infinito para detener el juego
    }

    // Verifica si han pasado 30 segundos y aún no se ha impreso "Nivel 2"
    if (!level2Printed && millis() - startTime >= 30000) {
      Serial.println("Nivel 2");
      score = 80; // Reinicia el puntaje a 80
      level2Printed = true; // Marca que se ha impreso "Nivel 2"
      tone(buzzerPin, 1500, 100); // Sonar el buzzer con doble tono (1500 Hz por 100 ms) al cambiar de nivel
      delay(100); // Pequeño retraso entre los tonos
      tone(buzzerPin, 2000, 100);
    }
    // Verifica si han pasado 60 segundos y aún no se ha impreso "Nivel 3"
    if (!level3Printed && millis() - startTime >= 60000) {
      Serial.println("Nivel 3");
      score = 100; // Reinicia el puntaje a 100
      level3Printed = true; // Marca que se ha impreso "Nivel 3"
      tone(buzzerPin, 1500, 100); // Sonar el buzzer con doble tono (1500 Hz por 100 ms) al cambiar de nivel
      delay(100); // Pequeño retraso entre los tonos
      tone(buzzerPin, 2000, 100);
    }
    if (score % 50 == 0) {
      if (currentDifficulty == FACIL && moleDisplayTime > 300)
        moleDisplayTime -= 200; // Aumenta la velocidad en 200ms con un límite máximo de 300ms
      if (currentDifficulty == NORMAL && moleDisplayTime > 300)
        moleDisplayTime -= 200; // Aumenta la velocidad en 200ms con un límite máximo de 300ms
      if (currentDifficulty == DIFICIL && moleDisplayTime > 300)
        moleDisplayTime -= 200; // Aumenta la velocidad en 200ms con un límite máximo de 300ms
    }
  }
}

void waitForDifficulty() {
  Serial.println("Por favor, seleccione la dificultad:");
  Serial.println("f - Fácil");
  Serial.println("n - Normal");
  Serial.println("d - Difícil");

  while (true) {
    if (Serial.available() > 0) {
      char input = Serial.read();
      if (input == 'f') {
        currentDifficulty = FACIL;
        score = 50;
        moleDisplayTime = baseMoleDisplayTime[FACIL]; // Utiliza el tiempo base de visualización del topo para el nivel fácil
        break;
      } else if (input == 'n') {
        currentDifficulty = NORMAL;
        score = 50;
        moleDisplayTime = baseMoleDisplayTime[NORMAL]; // Utiliza el tiempo base de visualización del topo para el nivel normal
        break;
      } else if (input == 'd') {
        currentDifficulty = DIFICIL;
        score = 50;
        moleDisplayTime = baseMoleDisplayTime[DIFICIL]; // Utiliza el tiempo base de visualización del topo para el nivel difícil
        break;
      }
    }
  }
}

int waitForInput() {
  unsigned long startTime = millis();
  while (millis() - startTime < 2000) { // Tiempo de espera para que el jugador responda (ajusta según sea necesario)
    for (int i = 0; i < numButtons; i++) {
      if (digitalRead(buttonPins[i]) == LOW) {
        return i; // Retorna el índice del botón que el jugador presiona
      }
    }
    if (Serial.available() > 0) {
      char input = Serial.read();
      if (input == 'f') {
        currentDifficulty = FACIL;
        score = 50;
        moleDisplayTime = baseMoleDisplayTime[FACIL]; // Utiliza el tiempo base de visualización del topo para el nivel fácil
      } else if (input == 'n') {
        currentDifficulty = NORMAL;
        score = 50;
        moleDisplayTime = baseMoleDisplayTime[NORMAL]; // Utiliza el tiempo base de visualización del topo para el nivel normal
      } else if (input == 'd') {
        currentDifficulty = DIFICIL;
        score = 50;
        moleDisplayTime = baseMoleDisplayTime[DIFICIL]; // Utiliza el tiempo base de visualización del topo para el nivel difícil
      }
      if (!printedDifficulty) {
        printDifficulty(currentDifficulty); // Imprime la nueva dificultad solo una vez al cambiarla
        printedDifficulty = true; // Marca que la dificultad se ha impreso
      }
    }
  }
  return -1; // Retorna -1 si el jugador no presiona ningún botón dentro del tiempo de espera
}

void displayScore() {
  // Mostrar el puntaje actual
  Serial.print("Score: ");
  Serial.println(score);
}

void setDifficulty(Difficulty difficulty) {
  // No es necesario cambiar el tiempo de visualización del topo aquí, ya que se ajusta en waitForDifficulty()
}

void printDifficulty(Difficulty difficulty) {
  switch (difficulty) {
    case FACIL:
      Serial.println("Dificultad: Fácil");
      break;
    case NORMAL:
      Serial.println("Dificultad: Normal");
      break;
    case DIFICIL:
      Serial.println("Dificultad: Difícil");
      break;
  }
}
