const int leds[] = {2, 3, 4, 5}; // store all the pin in array
const int arrayLength = 4;

void setup()
{
    for (int i = 0; i < arrayLength; i++)
    {
        pinMode(leds[i], OUTPUT);
    }
}

void loop()
{
    for (int i = 0; i < arrayLength; i++) //turn on in forward order
    {
        digitalWrite(leds[i], HIGH);
        delay(500);
        digitalWrite(leds[i], LOW);
    }

    for (int i = arrayLength - 2; i > 0; i--) //reverse
    {
        digitalWrite(leds[i], HIGH);
        delay(500);
        digitalWrite(leds[i], LOW);
    }
}