#include <SPI.h>
#include <SerialCommand.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <PID_v1.h>

#define ONE_WIRE_BUS 3
const int CS_DAC = 5;
char znak;
float temperature;
int cont_sensor_idx = 0;
double Input, Output;
double Kp=2000, Ki=100, Kd=1, Setpoint= 30;// Initial parameters

PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
SerialCommand SCmd;

void setup() {
  pinMode(CS_DAC, OUTPUT);
  digitalWrite(CS_DAC, HIGH);
  SPI.begin();
  Serial.begin(9600);
  sensors.begin();
  SCmd.addCommand("S",set_setpoint);
  SCmd.addCommand("S?",get_setpoint);
  SCmd.addCommand("P",set_p_gain);
  SCmd.addCommand("P?",get_p_gain);
  SCmd.addCommand("I",set_i_gain);
  SCmd.addCommand("I?",get_i_gain);
  SCmd.addCommand("D",set_d_gain);
  SCmd.addCommand("D?",get_d_gain);
  myPID.SetMode(AUTOMATIC);
  myPID.SetOutputLimits(0, 10000);
}

void loop() {
  //SCmd.readSerial(); 
  //sensors.requestTemperaturesByIndex(1);
  //Input = ((double)(printTempById(0)));
  sensors.requestTemperatures();
    for(int i=0;i<9;i++){
      SCmd.readSerial(); 
      temperature = printTempById(i);
      if(i==0){
        Input = ((double)(temperature));
      }
    }

  myPID.Compute();
  DAC_load((int) Output);
  //Serial.println(Input);
}

void DAC_load(int value) {                                    // Loads data to LTC1658 14-bit DAC through SPI
  Serial.println(String("H "+String(value)));
  //unsigned int value = 10000; // Serial.parseInt();            // Parses an int from the serial input
  value = value << 2;                                // Converts a 16-bit int to 14 bit
  byte byte1 = (unsigned int)(value >> 8);
  byte byte2 = (unsigned int)(value & 0xff);
  digitalWrite(CS_DAC, LOW);
  SPI.transfer(byte1);
  SPI.transfer(byte2);
  digitalWrite(CS_DAC, HIGH);
  //Serial.print("DAC word: ");
  //Serial.print(byte1, BIN);
  //Serial.println(byte2, BIN);
  
}

float printTempById(int index){
  temperature = sensors.getTempCByIndex(index);
  Serial.println(String("T"+String(index)+" "+String(temperature)));
  return temperature;
}

double read_float_arg(){
  char *arg;
  arg = SCmd.next(); 
  if (arg != NULL){
     return atof(arg);
  }
  return NULL;
}

void set_setpoint(){
  Setpoint = read_float_arg();
   Serial.println(String("#Temperature set to "+String(Setpoint)));
}

void set_p_gain(){
  Kp = read_float_arg();
  Serial.println(String("#P gain set to "+String(Kp)));
}

void set_i_gain(){
  Ki = read_float_arg();
  Serial.println(String("#I gain set to "+String(Ki)));
}

void set_d_gain(){
  Kd = read_float_arg();
  Serial.println(String("#D gain set to "+String(Kd)));
}

void get_setpoint(){
   Serial.println(String("S "+String(Setpoint)));
}

void get_p_gain(){
   Serial.println(String("P "+String(Kp)));
}

void get_i_gain(){
   Serial.println(String("I "+String(Ki)));
}

void get_d_gain(){
   Serial.println(String("D "+String(Kd)));
}
