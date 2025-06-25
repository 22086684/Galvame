const int ledPin = LED_BUILTIN;

const byte lichtsluisPin = 46;
const byte inductionPin = 48;
const byte KitKatInduction = 52;
const int relayPin = 50;
const int MEGA2RPi = 30;
const byte RPi2MEGA = 31;

const int pistonDraaierFORW = 11; 
const int pistonDraaierBACK = 10;
const int EXITloopbandFORW = 9;
const int EXITloopbandBACK = 8;
const int KitKatLoopbandFORW = 5;
const int KitKatLoopbandBACK = 4;
const int SchepLoopbandFORW = 7;
const int SchepLoopbandBACK = 6;
const int CorrigeerStavenFORW = 3;
const int CorrigeerStavenBACK = 2;

int PWM_pistonDraaier = 0;
int PWM_pistonDraaierFORW = 0;
int PWM_pistonDraaierBACK = 0;

int PWM_EXITloopband = 0;
int PWM_EXITloopbandFORW = 0;
int PWM_EXITloopbandBACK = 0;

int PWM_KitKatLoopband = 0;
int PWM_KitKatLoopbandFORW = 0;
int PWM_KitKatLoopbandBACK = 0;

int PWM_SchepLoopband = 0;
int PWM_SchepLoopbandFORW = 0;
int PWM_SchepLoopbandBACK = 0;

int PWM_CorrigeerStaven = 0;
int PWM_CorrigeerStavenFORW = 0;
int PWM_CorrigeerStavenBACK = 0;

bool bool_relayPin = 0;
bool pistonIncoming = 0;
bool inductionChecken = 0;
bool stopmetdraaien = 0;
bool wachtenOpPiston = 0;
bool processBezig = 0;
bool aanvoerGestopt = 0;
bool status_KitKat_Induction = LOW;
bool hijmoetstoppenalsdiehoogword = 0;
bool ermagweereentjekomen = 1;

int pistonTeller = 0;

//Timer declaren
unsigned long timerStart = 0;
bool timerRunning = false;
bool timerDone = false;
/*int eersteTimerWaarde = 1000; //Tijd van de timer zelf
int tweedeTimerWaarde = 1250;
int derdeTimerWaarde = 1500;
int vierdeTimerWaarde = 1750;
int vijfdeTimerWaarde = 2000;
int zesdeTimerWaarde = 2250;
int zevendeTimerWaarde = 2500;
int achsteTimerWaarde = 2750;
int negendeTimerWaarde = 3000;
int tiendeTimerWaarde = 3250;
int elfdeTimerWaarde = 3500;
int twaalfdeTimerWaarde = 3750;*/

//Tijd van de timer zelf
int halveTimerWaarde = 400;
int eersteTimerWaarde = 700; 
int eersteEnKwartTimerWaarde = 950;
int eersteEnHalveTimerWaarde = 1200;
int eersteEnDriekwartTimerWaarde = 1450;
int tweedeTimerWaarde = 1700;
int tweedeEnHalveTimerWaarde = 2100;
int derdeTimerWaarde = 2450;
int derdeEnHalveTimerWaarde = 2750;
int vierdeTimerWaarde = 3100;
int vierdeEnHalveTimerWaarde = 3400;
int vijfdeTimerWaarde = 3700;
int vijfdeEnHalveTimerWaarde = 3900;
int zesdeTimerWaarde = 4150;
int zesdeEnHalveTimerWaarde = 4400;
int zevendeTimerWaarde = 4600;
int zevendeEnHalveTimerWaarde = 4800;
int achsteTimerWaarde = 5050;
int achsteEnHalveTimerWaarde = 5300;
int negendeTimerWaarde = 5600;
int negendeEnHalveTimerWaarde = 5900;
int tiendeTimerWaarde = 6300;
int elfdeTimerWaarde = 6700;
int twaalfdeTimerWaarde = 7100;
int TimerTeLang = 9000;

// Timer variabelen
unsigned long timerDuration = 1500; // 1500 ms = 1.5 sec



void setup() {
  ledOn();
  Serial.begin(9600);
  delay(1000); // wachten tot seriële monitor klaar is

  PWM_EXITloopband = -255;
  draaiMotoren();
  delay(10000);
  PWM_EXITloopband = 0;
  draaiMotoren();

  // Set & Initialise pins
  setPinModes();
  initPins();
  

  //Prepare Program
  gripperOpen();
  draaiMotoren();
  ledOff();

  

  wachtenOpLichtSluis();

  
}

void loop() {
  // Hier kun je andere code kwijt, niks nodig voor nu
}

void wachtenOpLichtSluis() {
  ermagweereentjekomen = 1;
  pistonIncoming = 0;
  hijmoetstoppenalsdiehoogword = 0;
  ledOff();
  Serial.println("Wachten op vallende pistonRod");
  wachtenOpPiston = false;
  startAanvoer();
  delay(200);

  while (!wachtenOpPiston) {
    check_PistonAanvoer();
    bool statusLichtSluis = digitalRead(lichtsluisPin);
    if (statusLichtSluis == 0) {
      Serial.println("Piston gedetecteerd");
      wachtenOpPiston = true;
      timerStart = 0;
      timerRunning = false;
      timerDone = false;
    }
  }

  processPiston();
}

void processPiston() {
  ledOff();
  processBezig = 1;
  startTimer(500); // Value timer [ms]
  while (!isTimerDone()) {
    // Hier kun je code draaien terwijl je wacht
    check_PistonAanvoer();
  }

  PWM_EXITloopband = -255;
  draaiMotoren();
  startTimer(200); // Value timer [ms]
  while (!isTimerDone()) {
    // Hier kun je code draaien terwijl je wacht
    check_PistonAanvoer();
  }

  PWM_EXITloopband = 0;
  draaiMotoren();
  startTimer(20); // Value timer [ms]
  while (!isTimerDone()) {
    // Hier kun je code draaien terwijl je wacht
    check_PistonAanvoer();
  }

  Serial.println("Gripper dicht...");
  gripperDicht();
  startTimer(200); // Value timer [ms]
  while (!isTimerDone()) {
    // Hier kun je code draaien terwijl je wacht
    check_PistonAanvoer();

    Serial.println("Timer is bezig...");
  }

  PWM_pistonDraaier = 14;
  draaiMotoren();
  /*startTimer(20); // Value timer [ms]
  while (!isTimerDone()) {
    // Hier kun je code draaien terwijl je wacht
    check_PistonAanvoer();

    Serial.println("Timer is bezig...");
  }*/

  stopmetdraaien = false;

  Serial.println("Wacht op metaal weg (overgang HIGH -> LOW)...");
  bool vorigeStatus = HIGH;
  while (!stopmetdraaien) {
    
    // Timer starten (alleen één keer)
    if (!timerRunning && !timerDone) {
      timerStart = millis();
      timerRunning = true;
      Serial.println("Timer gestart!");
    }
    check_PistonAanvoer();

    // Check of timer voorbij is
    if (timerRunning && (millis() - timerStart >= halveTimerWaarde)) {
      PWM_pistonDraaier = 15; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= eersteTimerWaarde)) {
      PWM_pistonDraaier = 16; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= eersteEnKwartTimerWaarde)) {
      PWM_pistonDraaier = 17; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= eersteEnHalveTimerWaarde)) {
      PWM_pistonDraaier = 18; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= eersteEnDriekwartTimerWaarde)) {
      PWM_pistonDraaier = 19; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= tweedeTimerWaarde)) {
      PWM_pistonDraaier = 20; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= tweedeEnHalveTimerWaarde)) {
      PWM_pistonDraaier = 21; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= derdeTimerWaarde)) {
      PWM_pistonDraaier = 22; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= derdeEnHalveTimerWaarde)) {
      PWM_pistonDraaier = 23; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= vierdeTimerWaarde)) {
      PWM_pistonDraaier = 24; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= vierdeEnHalveTimerWaarde)) {
      PWM_pistonDraaier = 25; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= vijfdeTimerWaarde)) {
      PWM_pistonDraaier = 26; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= vijfdeEnHalveTimerWaarde)) {
      PWM_pistonDraaier = 27; // Of een andere waarde die je wilt zetten
    }        
    if (timerRunning && (millis() - timerStart >= zesdeTimerWaarde)) {
      PWM_pistonDraaier = 28; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= zesdeEnHalveTimerWaarde)) {
      PWM_pistonDraaier = 29; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= zevendeTimerWaarde)) {
      PWM_pistonDraaier = 30; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= zevendeEnHalveTimerWaarde)) {
      PWM_pistonDraaier = 31; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= achsteTimerWaarde)) {
      PWM_pistonDraaier = 32; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= achsteEnHalveTimerWaarde)) {
      PWM_pistonDraaier = 33; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= negendeTimerWaarde)) {
      PWM_pistonDraaier = 34; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= negendeEnHalveTimerWaarde)) {
      PWM_pistonDraaier = 35; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= tiendeTimerWaarde)) {
      PWM_pistonDraaier = 37; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= elfdeTimerWaarde)) {
      PWM_pistonDraaier = 39; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= twaalfdeTimerWaarde)) {
      PWM_pistonDraaier = 41; // Of een andere waarde die je wilt zetten
    }
    if (timerRunning && (millis() - timerStart >= TimerTeLang)) {
      PWM_pistonDraaier = 60; // Of een andere waarde die je wilt zetten
      ledOn();
    }
    draaiMotoren();

    

    bool huidigeStatus = digitalRead(inductionPin);
    if (vorigeStatus == HIGH && huidigeStatus == HIGH) {
      Serial.println("Metaal weg, motor stoppen.");
      stopmetdraaien = true;
      PWM_pistonDraaier = 0;
      draaiMotoren();

      //Check of hij iets langer door moet draaien
      if (timerRunning && (millis() - timerStart >= 75) && (millis() - timerStart < 700)) {
        Serial.println("Timer afgelopen, variabele aangepast!");
        PWM_pistonDraaier = 14;
        draaiMotoren();
        startTimer(50); // Value timer [ms]
        while (!isTimerDone()) {
          // Hier kun je code draaien terwijl je wacht
          check_PistonAanvoer();
        }
        PWM_pistonDraaier = 0;
        draaiMotoren();
      }
      //Timer uitzetten
      timerRunning = false;
      timerDone = true;   // Timer is "klaar", zal nu genegeerd worden
      vorigeStatus = huidigeStatus;
    }
    //check of de aanvoer gestopt moet worden
    check_PistonAanvoer();
  }
  gripperOpen();
  pistonTeller++;
  if (pistonTeller == 5) {
    pistonTeller = 0;
    EXITloopband_Vol();
  }
  check_PistonAanvoer();
  EXITloopband_Opschuiven();
}

void EXITloopband_Opschuiven() {
  Serial.println("loopband één cylinder opschuiven");
  PWM_EXITloopband = -255;
  draaiMotoren();
  startTimer(815); // Value timer [ms]
  while (!isTimerDone()) {
    // Hier kun je code draaien terwijl je wacht
    check_PistonAanvoer();
  }
  PWM_EXITloopband = 0;
  draaiMotoren();
  processBezig = 0;
  wachtenOpLichtSluis();
}

void EXITloopband_Vol() {
  Serial.println("5 pistons naar einde bewegen");
  PWM_EXITloopband = -255;
  draaiMotoren();
  startTimer(3337); // Value timer [ms]
  while (!isTimerDone()) {
    // Hier kun je code draaien terwijl je wacht
    check_PistonAanvoer();

    Serial.println("Timer is bezig...");
  }
  PWM_EXITloopband = 0;
  draaiMotoren();
  ready2pick();

  int getStatus_RPi = digitalRead(RPi2MEGA);
  while (!getStatus_RPi) {
    check_PistonAanvoer();
    getStatus_RPi = digitalRead(RPi2MEGA);
  }

  notReady2pick();
  ledOff();
  initPins();
  wachtenOpLichtSluis();
}

void check_PistonAanvoer () {
  status_KitKat_Induction = digitalRead(KitKatInduction);
  Serial.println("InductionStatus is:");
  Serial.println(status_KitKat_Induction);
  if (pistonIncoming == 1 && status_KitKat_Induction == HIGH) {
    hijmoetstoppenalsdiehoogword = 1;
    ledOn();
  }
  if (ermagweereentjekomen == 1 && status_KitKat_Induction == LOW) {
    pistonIncoming = 1;
    ermagweereentjekomen = 0;
  }
  if (hijmoetstoppenalsdiehoogword == 1 && status_KitKat_Induction == LOW && ermagweereentjekomen == 0) {
    stopAanvoer();
    aanvoerGestopt = 1;
    hijmoetstoppenalsdiehoogword = 0;
  }
}

void stopAanvoer () {
  PWM_SchepLoopband = 0;
  PWM_KitKatLoopband = 0;
  PWM_CorrigeerStaven = 0;
  draaiMotoren();
}

void startAanvoer () {
  PWM_SchepLoopband = -230;
  PWM_KitKatLoopband = -180;
  PWM_CorrigeerStaven = -200;
  draaiMotoren();
}

// Functie om de timer te starten
void startTimer(unsigned long duration) {
  timerStart = millis();
  timerDuration = duration;
}

// Functie om te checken of de timer klaar is
bool isTimerDone() {
  return (millis() - timerStart >= timerDuration);
}

//------------------------------------------------------------------------------------------------------------------------------------------------------
//Hieronder niks interessants meer

void ready2pick () {
  digitalWrite(MEGA2RPi, HIGH);
}

void notReady2pick () {
  digitalWrite(MEGA2RPi, LOW);
}

void ledOn () {
  digitalWrite(ledPin, HIGH);
}

void ledOff () {
  digitalWrite(ledPin, LOW);
}

void gripperOpen () {
  digitalWrite(relayPin, HIGH);
}

void gripperDicht () {
  digitalWrite(relayPin, LOW);
}

void toggleRelay () {
  if (bool_relayPin == 0) {
    bool_relayPin = 1;
    digitalWrite(relayPin, HIGH);
  }
  else {
    bool_relayPin = 0;
    digitalWrite(relayPin, LOW);
  }
}

void setPinModes () {
  pinMode(pistonDraaierFORW, OUTPUT);
  pinMode(pistonDraaierBACK, OUTPUT);
  pinMode(EXITloopbandFORW, OUTPUT);
  pinMode(EXITloopbandBACK, OUTPUT);
  pinMode(KitKatLoopbandFORW, OUTPUT);
  pinMode(KitKatLoopbandBACK, OUTPUT);
  pinMode(SchepLoopbandFORW, OUTPUT);
  pinMode(SchepLoopbandBACK, OUTPUT);
  pinMode(CorrigeerStavenFORW, OUTPUT);
  pinMode(CorrigeerStavenBACK, OUTPUT);

  pinMode(ledPin, OUTPUT);
  pinMode(relayPin, OUTPUT);

  pinMode(49, OUTPUT);
  pinMode(51, OUTPUT);
  pinMode(44, OUTPUT);
  pinMode(53, OUTPUT);
  pinMode(MEGA2RPi, OUTPUT);

  pinMode(RPi2MEGA, INPUT);
  pinMode(inductionPin, INPUT_PULLUP);
  pinMode(lichtsluisPin, INPUT);
  pinMode(KitKatInduction, INPUT_PULLUP);
}

void initPins () {
  digitalWrite(49, HIGH);
  digitalWrite(51, HIGH);
  digitalWrite(44, HIGH);
  digitalWrite(53, HIGH);

  PWM_SchepLoopband = -255;
  PWM_KitKatLoopband = -180;
  PWM_CorrigeerStaven = -250;
  draaiMotoren();
}

void draaiMotoren() {
  if (PWM_pistonDraaier >= 0) {
    PWM_pistonDraaierFORW = PWM_pistonDraaier;
    PWM_pistonDraaierBACK = 0;
  } else {
    PWM_pistonDraaierFORW = 0;
    PWM_pistonDraaierBACK = -PWM_pistonDraaier;
  }
  analogWrite(pistonDraaierFORW, PWM_pistonDraaierFORW);
  analogWrite(pistonDraaierBACK, PWM_pistonDraaierBACK);

  if (PWM_EXITloopband >= 0) {
    PWM_EXITloopbandFORW = PWM_EXITloopband;
    PWM_EXITloopbandBACK = 0;
  } else {
    PWM_EXITloopbandFORW = 0;
    PWM_EXITloopbandBACK = -PWM_EXITloopband;
  }
  analogWrite(EXITloopbandFORW, PWM_EXITloopbandFORW);
  analogWrite(EXITloopbandBACK, PWM_EXITloopbandBACK);
  if (PWM_KitKatLoopband >= 0) {
    PWM_KitKatLoopbandFORW = PWM_KitKatLoopband;
    PWM_KitKatLoopbandBACK = 0;
  } else {
    PWM_KitKatLoopbandFORW = 0;
    PWM_KitKatLoopbandBACK = -PWM_KitKatLoopband;
  }
  analogWrite(KitKatLoopbandFORW, PWM_KitKatLoopbandFORW);
  analogWrite(KitKatLoopbandBACK, PWM_KitKatLoopbandBACK);
  if (PWM_SchepLoopband >= 0) {
    PWM_SchepLoopbandFORW = PWM_SchepLoopband;
    PWM_SchepLoopbandBACK = 0;
  } else {
    PWM_SchepLoopbandFORW = 0;
    PWM_SchepLoopbandBACK = -PWM_SchepLoopband;
  }
  analogWrite(SchepLoopbandFORW, PWM_SchepLoopbandFORW);
  analogWrite(SchepLoopbandBACK, PWM_SchepLoopbandBACK);
  if (PWM_CorrigeerStaven >= 0) {
    PWM_CorrigeerStavenFORW = PWM_CorrigeerStaven;
    PWM_CorrigeerStavenBACK = 0;
  } else {
    PWM_CorrigeerStavenFORW = 0;
    PWM_CorrigeerStavenBACK = -PWM_CorrigeerStaven;
  }
  analogWrite(CorrigeerStavenFORW, PWM_CorrigeerStavenFORW);
  analogWrite(CorrigeerStavenBACK, PWM_CorrigeerStavenBACK);
}
