//-------------------------------------------------------------------------------------------------------------------------
// Heating plate temperature controller Revision: 1.0
//
// Software version: 1.0 16/02/2017
//          Authors: J. Rutkowski and V. Maurice
//      Description: PID temperature controller, uses nine DS18B20 temperature sensors as input and a AD5391 DAC as output.
//                   The power stage, driven by the DAC, is composed of nine LT3092 Programmable Current Sources.
//         Comments: A temperature gradient can be induced on the heating plate by modifying the offset of individual DAC
//                   channels using the writeDACoffset() function.
//    Modifications: none
//-------------------------------------------------------------------------------------------------------------------------


#include <SPI.h>
#include <SerialCommand.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <PID_v1.h>

#define ONE_WIRE_BUS 5
const int CS_DAC = 4;
const int LDAC = 3;
const int CLR = 2;
float temperature;
int cont_sensor_idx = 0;
double Input, Output;
double Kp=20, Ki=1.5, Kd=5, Setpoint= 30;                     // Initial PID and setpoint parameters
int ratios[9];
unsigned int heater_value;

PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
SerialCommand SCmd;

void setup() {
  for (int i = 0; i < 9; i++){
    ratios[i] = 32;
  }
  pinMode(CS_DAC, OUTPUT);                                    // DAC initialization
  pinMode(LDAC, OUTPUT);
  pinMode(CLR, OUTPUT);
  digitalWrite(CS_DAC, HIGH);
  digitalWrite(LDAC, HIGH);
  digitalWrite(CLR, HIGH);
  Serial.begin(115200);
  SPI.begin();
  SPI.setDataMode(SPI_MODE1);
  setDACconfigReg();
  writeDACgainAllChan(0x7FE);
  writeDACoffsetAllChan(0x800);

  sensors.begin();                                            // PID and sensors initialization
  SCmd.addCommand("S",set_setpoint);
  SCmd.addCommand("S?",get_setpoint);
  SCmd.addCommand("P",set_p_gain);
  SCmd.addCommand("P?",get_p_gain);
  SCmd.addCommand("I",set_i_gain);
  SCmd.addCommand("I?",get_i_gain);
  SCmd.addCommand("D",set_d_gain);
  SCmd.addCommand("D?",get_d_gain);
  SCmd.addCommand("R",set_power_ratio);
  SCmd.addCommand("R?",get_power_ratio);
  SCmd.addCommand("A?",get_all_parameters);
  myPID.SetMode(AUTOMATIC);
  //myPID.SetOutputLimits(0, 4095);
  myPID.SetOutputLimits(0, 127);
}


void loop() {
  SCmd.readSerial(); 
  sensors.requestTemperatures();
    for(int i=0;i<9;i++){                                     // Get all temperatures
      temperature = printTempById(i);
      if(i==0){
        Input = ((double)(temperature));
      }
    }
  myPID.Compute();                                            // Compute the PID and apply correction to DAC
  writeDACdataAllChan((int) Output);
  Serial.println(String("H "+String(Output)));
}


// -------------------------------------- AD5391 DAC related functions ------------------------------------------------------

void writeDACdataAllChan(unsigned int value){                   // Loads the DAC data registers of 9 DACs (0-8) with the same value, takes the value as input
  for (int i = 0; i < 9; i++){
    heater_value = value*ratios[i];
    writeDACdata(i,heater_value) ; 
    //Serial.println(String("#P"+String(i)+" "+String(heater_value)));
    //writeDACdata(i, value); 
  }
}

void writeDACgainAllChan(unsigned int value){                   // Loads the DAC gain registers of 9 DACs (0-8) with the same value, takes the value as input
  for (int i = 0; i <= 9; i++){
    writeDACgain(i, value); 
  }
}

void writeDACoffsetAllChan(unsigned int value){                 // Loads the DAC offset registers of 9 DACs (0-8) with the same value, takes the value as input
  for (int i = 0; i <= 9; i++){
    writeDACoffset(i, value); 
  }
}

void setDACconfigReg(){
  digitalWrite(CS_DAC, LOW);                                    //Configures the control register
  SPI.transfer(B00001100);
  SPI.transfer(B00000100);
  SPI.transfer(B00000000);
  digitalWrite(CS_DAC, HIGH);
}

void writeDACdata(unsigned int chanNum, unsigned int value) {   // Loads the DAC data register, takes channel number (0-8) and value as input         
  value = value << 2;
  byte byte1 = chanNum;
  byte byte2 = ((value >> 8) | 0xC0);
  byte byte3 = (value & 0xff);
  digitalWrite(CS_DAC, LOW);
  SPI.transfer(byte1);
  SPI.transfer(byte2);
  SPI.transfer(byte3);
  digitalWrite(CS_DAC, HIGH);
  digitalWrite(LDAC, LOW);
  digitalWrite(LDAC, HIGH);
}

void writeDACgain(unsigned int chanNum, unsigned int gain){    // Loads the DAC gain register, takes channel number (0-8) and value as input
  gain = gain << 2;
  byte byte1 = chanNum;
  byte byte2 = ((gain >> 8) | 0x40);
  byte byte3 = (gain & 0xff);
  digitalWrite(CS_DAC, LOW);
  SPI.transfer(byte1);
  SPI.transfer(byte2);
  SPI.transfer(byte3);
  digitalWrite(CS_DAC, HIGH);
  digitalWrite(LDAC, LOW);
  digitalWrite(LDAC, HIGH);
}

void writeDACoffset(unsigned int chanNum, unsigned int offset){  // Loads the DAC offset register, takes channel number (0-8) and value as input
  offset = offset << 2;
  byte byte1 = chanNum;
  byte byte2 = ((offset >> 8) | 0x80);
  byte byte3 = (offset & 0xff);
  digitalWrite(CS_DAC, LOW);
  SPI.transfer(byte1);
  SPI.transfer(byte2);
  SPI.transfer(byte3);
  digitalWrite(CS_DAC, HIGH);
  digitalWrite(LDAC, LOW);
  digitalWrite(LDAC, HIGH);
}


//--------------------------------------- Seial interface related functions ------------------------------------------------

float printTempById(int index){                               // Reads and prints the temparature value to the output, adds "T" for serial parsing. Returns the temperature value (float), takes the sensor index as input (int).
  temperature = sensors.getTempCByIndex(index);
  Serial.println(String("T"+String(index)+" "+String(temperature)));
  return temperature;
}

double read_float_arg(){                                      // Parses a double from the serial input. Returns the value (double).
  char *arg;
  arg = SCmd.next(); 
  if (arg != NULL){
     return atof(arg);
  }
  return 0;
}

void set_setpoint(){                                          // Sets regulation setpoint.
  Setpoint = read_float_arg();
   Serial.println(String("#Temperature set to "+String(Setpoint)));
}

void set_p_gain(){                                            // Sets the proportional gain of the PID
  Kp = read_float_arg();
  myPID.SetTunings(Kp, Ki, Kd);
  Serial.println(String("#P gain set to "+String(Kp)));
}

void set_i_gain(){                                            // Sets the integral gain of the PID
  Ki = read_float_arg();
  myPID.SetTunings(Kp, Ki, Kd);
  Serial.println(String("#I gain set to "+String(Ki)));
}

void set_d_gain(){                                           // Sets the differentioa gain of the PID
  Kd = read_float_arg();
  myPID.SetTunings(Kp, Ki, Kd);
  Serial.println(String("#D gain set to "+String(Kd)));
}

void set_power_ratio(){
  int chan_number;
  char *arg;
  arg = SCmd.next();
  if (arg != NULL) {
    chan_number = atoi(arg);
    arg = SCmd.next();
    if (arg != NULL && chan_number<9 && chan_number>=0){
        ratios[chan_number] = atof(arg);
        Serial.println(String("#R ratio "+String(chan_number)+" set to "+String(ratios[chan_number])));
    }
  }
}

void get_all_power_ratios(){
    for(int i=0;i<9;i++){
      Serial.println(String("R "+String(i)+" "+String(ratios[i])));
    }  
}

void get_power_ratio(){
  int chan_number;
  char *arg;
  arg = SCmd.next();
  if (arg != NULL) {
    chan_number = atoi(arg);
    if (chan_number<9 && chan_number>=0){
      Serial.println(String("R "+String(chan_number)+" "+String(ratios[chan_number])));
    }
  }
}


void get_setpoint(){
   Serial.println(String("S "+String(Setpoint)));            // Prints the setpoint
}

void get_p_gain(){
   Serial.println(String("P "+String(Kp)));                  // Prints the proportional gain
}

void get_i_gain(){
   Serial.println(String("I "+String(Ki)));                  // Prints the integral gain
}

void get_d_gain(){
   Serial.println(String("D "+String(Kd)));                  // Prints the differential gain
}

void get_all_parameters(){
  get_p_gain();
  get_i_gain();
  get_d_gain();
  get_setpoint();
  get_all_power_ratios();
}
