#include <Adafruit_NeoPixel.h>
#include <SerialCommand.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif
#define PIN 6
#define NUMPIXELS 16
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
// how much serial data we expect before a newline
int red=255;
int green=255;
int blue=255;
bool  enabled=false;
SerialCommand SCmd;

void setup() {
  // Initialize all pixels to 'off'
  pixels.begin();
  pixels.show();
  Serial.begin(9600);
  SCmd.addCommand("R",set_red);
  SCmd.addCommand("R?",get_red);
  SCmd.addCommand("G",set_green);
  SCmd.addCommand("G?",get_green);
  SCmd.addCommand("B",set_blue);
  SCmd.addCommand("B?",get_blue);
  SCmd.addCommand("E",set_enabled);
  SCmd.addCommand("E?",get_enabled);
}

void loop() {
  SCmd.readSerial();
  
}

double read_int_arg(){                                      // Parses a double from the serial input. Returns the value (double).
  char *arg;
  arg = SCmd.next(); 
  if (arg != NULL){
     return atoi(arg);
  }
  return 0;
}

void set_red(){
  red = read_int_arg();
  setAllPixels();
}

void get_red(){
   Serial.println(String("R "+String(red)));
}

void set_green(){
  green = read_int_arg();
  setAllPixels();
}

void get_green(){
   Serial.println(String("G "+String(green)));
}

void set_blue(){
  blue = read_int_arg();
  setAllPixels();
}

void get_blue(){
   Serial.println(String("B "+String(blue)));
}

void set_enabled(){
  if(read_int_arg()>0){
    enabled = true;
  }
  else{
    enabled = false;
  }
  setAllPixels();
}

void get_enabled(){
   Serial.println(String("E "+String(int(enabled))));
}

void setAllPixels(){
  for(int i=0;i<NUMPIXELS;i++){
    // pixels.Color takes RGB values, from 0,0,0 up to 255,255,255
    if(enabled){pixels.setPixelColor(i, pixels.Color(red,green,blue));}
    else{pixels.setPixelColor(i, pixels.Color(0,0,0));}
    pixels.show(); // This sends the updated pixel color to the hardware.
  }
}
