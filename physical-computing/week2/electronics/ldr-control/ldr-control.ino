const int ledPin = 9;
const int ldrPin = A0;

void setup()
{
    pinMode(ledPin, OUTPUT);
    Serial.begin(9600);
}

void loop()
{
    int lightValue = analogRead(ldrPin); // store the LDR sensor reading
    Serial.println(lightValue); // print the sensor value to determine the threshold

    if (lightValue > 1010)
    {
        digitalWrite(ledPin, HIGH); // turn on when greater than 1010 
    }
    else
    {
        digitalWrite(ledPin, LOW); // turn off when lesser
    }

    delay(1000);
}