#include <Servo.h>

Servo eyeServo;
Servo browServo;
Servo mouthServo;

const int EYE_PIN = 9;
const int BROW_PIN = 10;
const int MOUTH_PIN = 11;

// Servo angle settings for eye movement
const int EYE_OPEN = 90;
const int EYE_CLOSED = 180;

// Servo angle settings for eyebrow movement
const int BROW_NORMAL = 60;
const int BROW_RAISED = 100;

// Servo angle settings for mouth movement
const int MOUTH_CLOSED = 40;
const int MOUTH_OPEN = 130;

unsigned long lastValidCommand = 0;
bool atDefault = true;

// Return all facial features to their neutral positions
void returnToDefault() {
  eyeServo.write(EYE_OPEN);
  browServo.write(BROW_NORMAL);
  mouthServo.write(MOUTH_CLOSED);
  atDefault = true;
}

void setup() {
  // Start serial communication with p5.js
  Serial.begin(115200);

  // Attach each servo to its assigned Arduino pin
  eyeServo.attach(EYE_PIN);
  browServo.attach(BROW_PIN);
  mouthServo.attach(MOUTH_PIN);

  // Set the initial facial expression to neutral
  eyeServo.write(EYE_OPEN);
  browServo.write(BROW_NORMAL);
  mouthServo.write(MOUTH_CLOSED);
}

void loop() {
  if (!atDefault && millis() - lastValidCommand >= 1500UL) {
    returnToDefault();
  }

  if (Serial.available()) {

    // Receive expression states from p5.js as a string
    // Example: "1,0,1"
    String data = Serial.readStringUntil('\n');
    data.trim();

    int eyesClosed;
    int browsRaised;
    int mouthOpen;

    // Split the p5.js string into three Arduino values:
    // eyesClosed, browsRaised, mouthOpen
    int result = sscanf(
      data.c_str(),
      "%d,%d,%d",
      &eyesClosed,
      &browsRaised,
      &mouthOpen
    );

    // Make sure all three values were received correctly
    // and each value is either 0 or 1
    if (result == 3 &&
        (eyesClosed == 0 || eyesClosed == 1) &&
        (browsRaised == 0 || browsRaised == 1) &&
        (mouthOpen == 0 || mouthOpen == 1)) {
      lastValidCommand = millis();
      atDefault = (eyesClosed == 0 && browsRaised == 0 && mouthOpen == 0);

      // Eye
      if (eyesClosed == 1) {
        eyeServo.write(EYE_CLOSED);
      } else {
        eyeServo.write(EYE_OPEN);
      }

      // Brows
      if (browsRaised == 1) {
        browServo.write(BROW_RAISED);
      } else {
        browServo.write(BROW_NORMAL);
      }

      // Mouth
      if (mouthOpen == 1) {
        mouthServo.write(MOUTH_OPEN);
      } else {
        mouthServo.write(MOUTH_CLOSED);
      }
    }
  }
}