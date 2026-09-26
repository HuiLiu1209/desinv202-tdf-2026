int led = 13;
void setup()
{
    Serial.begin(9600);
    pinMode(led, OUTPUT);
}

void loop()
{
    digitalWrite(led, HIGH);
    Serial.println("Hello World");
    delay(1000);
    digitalWrite(led, LOW);
    delay(1000);
}