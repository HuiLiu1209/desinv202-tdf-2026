#include <Servo.h> //import servo motor library

const int trigPin = 8;   // ultrasound trig pin
const int echoPin = 9;   // ultrasound echo pin
const int servoPin = 10; // servo motor signal pin

Servo myServo;

void setup()
{
    // put your setup code here, to run once:
    pinMode(trigPin, OUTPUT);
    pinMode(echoPin, INPUT);
    myServo.attach(servoPin); // connect servo signal pin
    Serial.begin(9600);       // debug purpose
}

void loop()
{
    // put your main code here, to run repeatedly:

    // ultrasound sensor module
    // send 10 μs trigger pulse to start distance measurement
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);

    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);

    digitalWrite(trigPin, LOW);

    long duration = pulseIn(echoPin, HIGH); // get duration time
    float distance = duration * 0.034 / 2;  // muliply sound velocity to get disntance

    Serial.println(distance);

    // servo motor module
    // ctrl servo motor
    if (distance < 20)
    {
        myServo.write(90);
    }
    else
    {
        myServo.write(0);
    }

    delay(100);
}