//#include <SoftwareSerial.h>
#include <SerialCommand.h>
SerialCommand SCmd;   // The demo SerialCommand object

int power = 255;
int stbPow = 0;
int stepIndex = 0;
int counter = 0;
unsigned long currentMillis;
long previousMillis = 0; 
long interval = 10;
int set_point = 0;
int dir = 0;

void setup() {
  
  //establish motor direction toggle pins
  pinMode(12, OUTPUT); //CH A -- HIGH = forwards and LOW = backwards???
  pinMode(13, OUTPUT); //CH B -- HIGH = forwards and LOW = backwards???
  
  //establish motor brake pins
  pinMode(9, OUTPUT); //brake (disable) CH A
  pinMode(8, OUTPUT); //brake (disable) CH B
  Serial.begin(19200);

  SCmd.addCommand("P",setPosition);
  SCmd.addCommand("P?",getPosition);
  SCmd.setDefaultHandler(unrecognized);
}

double read_float_arg(){
  char *arg;
  arg = SCmd.next(); 
  if (arg != NULL){
     return atof(arg);
  }
}


void moveOneStep(){
    if(dir>0){
      counter = counter +1;
      stepIndex=(stepIndex+1)%4;
    }
    else{
      counter = counter -1;
      stepIndex=(stepIndex+3)%4;
    }
    switch (stepIndex) {
      case 0:
        digitalWrite(9, LOW);  //ENABLE CH A
        digitalWrite(8, HIGH); //DISABLE CH B
        digitalWrite(12, HIGH);   //Sets direction of CH A
        analogWrite(3, power);   //Moves CH A
        //Serial.println(String("Pos A (|) :"+String(counter)));
        break;
      case 1:
        digitalWrite(9, HIGH);  //DISABLE CH A
        digitalWrite(8, LOW); //ENABLE CH B
        digitalWrite(13, LOW);   //Sets direction of CH B
        analogWrite(11, power);   //Moves CH B
        //Serial.println(String("Pos B (/) :"+String(counter)));
        break;
      case 2:        
        digitalWrite(9, LOW);  //ENABLE CH A
        digitalWrite(8, HIGH); //DISABLE CH B
        digitalWrite(12, LOW);   //Sets direction of CH A
        analogWrite(3, power);   //Moves CH A
        //Serial.println(String("Pos C (-) :"+String(counter)));
        break;
      case 3:        
        digitalWrite(9, HIGH);  //DISABLE CH A
        digitalWrite(8, LOW); //ENABLE CH B
        digitalWrite(13, HIGH);   //Sets direction of CH B
        analogWrite(11, power);   //Moves CH B 
        //Serial.println(String("Pos D (\\) :"+String(counter)));
        break;
     }
     //Serial.println(String("Pos: "+String(counter)));
}

void standby(){
     analogWrite(11, stbPow);   //Moves CH B
     analogWrite(3, stbPow);   //Moves CH A
}

void getPosition(){
  Serial.println(counter);
}

void setPosition(){
  set_point = read_float_arg();
}

void unrecognized(const char *command){
  Serial.println("What?"); 
}

void loop(){
  SCmd.readSerial();
  currentMillis = millis();
  if(currentMillis - previousMillis > interval) {
    previousMillis = currentMillis;
    if(set_point>counter){
      dir = 1 ;
      moveOneStep();
    }
    if(set_point<counter){
      dir = 0 ;
      moveOneStep();
    }
    if(set_point==counter){
      standby();
    }
  }
}

