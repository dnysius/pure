#include <Wire.h>
#include <Adafruit_MotorShield.h>

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
// Or, create it with a different I2C address (say for stacking)
// Adafruit_MotorShield AFMS = Adafruit_MotorShield(0x61); 

// Connect a stepper motor with 200 steps per revolution (1.8 degree)
// to motor port #2 (M3 and M4)
Adafruit_StepperMotor *myMotor = AFMS.getStepper(200, 2);
  int totalcount = 0;  
  String inString = "";     

void setup() {
  Serial.begin(9600);           // set up Serial library at 9600 bps
  AFMS.begin();  // create with the default frequency 1.6KHz
  //AFMS.begin(1000);  // OR with a different frequency, say 1KHz
  
  myMotor->setSpeed(10);  // 10 rpm   
  Serial.println("Enter number of steps. Each step is 10um. Negative number for opposite direction.");
  Serial.println("Start Position: 0");
}

void loop() {
   inString = Serial.readStringUntil('\n');      //reads written string, stops when enter is pressed
  if (inString.toInt() != 0) {                    //makes sure a number is entered as the string
    myMotor->step(inString.toInt(), BACKWARD, DOUBLE);
    totalcount += inString.toInt();               //adds the steps moved to the posotion tracker
    Serial.println("Moved " + String(inString.toInt(), DEC) + " steps to " + String(totalcount, DEC));   //reports the move and the new position (relative to 0)
    inString = "";                                //clears input string
  }
}
