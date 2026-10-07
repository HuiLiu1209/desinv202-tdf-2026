#include <Adafruit_NeoPixel.h>

const int LED_PIN = 13;
const int LED_COUNT = 64;
const int MAX_BRIGHTNESS = 3;
const int STEP_DELAY_MS = 150;

Adafruit_NeoPixel matrix(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  matrix.begin();
  matrix.setBrightness(MAX_BRIGHTNESS);
  matrix.clear();
  matrix.show();
}

void loop() {
  // 按灯珠编号走一遍；蛇形接线的 Matrix 会逐行交替方向。
  for (int led = 0; led < LED_COUNT; led++) {
    matrix.setPixelColor(led, matrix.Color(255, 255, 255));
    matrix.show();
    delay(STEP_DELAY_MS);

    matrix.setPixelColor(led, 0);
    matrix.show();
    delay(STEP_DELAY_MS);
  }
}
