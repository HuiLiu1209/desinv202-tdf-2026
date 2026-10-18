#include <Adafruit_NeoPixel.h>
#include "tide_data.h"

// Hardware: Adafruit Feather ESP32 V2, 64 NeoPixels, DIN -> GPIO 13.
constexpr uint8_t LED_PIN = 13;
constexpr uint8_t MAX_BRIGHTNESS = 10;  // NeoPixel global limit, 0..255.
constexpr uint32_t FRAME_DELAY_MS = 63; // 96 samples x 63 ms = 6.048 s/day.
constexpr uint32_t RENDER_INTERVAL_MS = 20;

// Dates follow physical LED order: day 0 is oldest, day 63 is most recent.
Adafruit_NeoPixel matrix(TIDE_DAYS, LED_PIN, NEO_GRB + NEO_KHZ800);
uint32_t lastFrameAt = 0;
uint32_t lastRenderAt = 0;
uint8_t frame = 0;

float tideAt(uint8_t day, uint8_t sample) {
  // Read a signed tide height in millimeters from flash memory.
  return static_cast<int16_t>(pgm_read_word(&TIDE_MM[day][sample]));
}

void renderFrame(float blend) {
  // All dates share one playback clock; adjacent 15-minute predictions are interpolated.
  // Hold the final 23:45 sample until the cycle restarts at 00:00.
  const uint8_t next = frame + 1 < TIDE_SAMPLES_PER_DAY ? frame + 1 : frame;
  for (uint8_t day = 0; day < TIDE_DAYS; ++day) {
    const float tide = tideAt(day, frame) * (1.0f - blend) + tideAt(day, next) * blend;
    const float normalized = constrain(
        (tide - TIDE_MIN_MM) / (TIDE_MAX_MM - TIDE_MIN_MM), 0.0f, 1.0f);
    // Squared intensity dims low tides; the shared range allows comparisons by date.
    const float intensity = normalized * normalized;
    const uint8_t level = static_cast<uint8_t>(intensity * 255.0f + 0.5f);
    // Tide height controls a deep blue -> cyan -> pale cyan-white color gradient.
    // The blue channel sets the peak RGB level; red and green determine the hue.
    const float red = normalized <= 0.5f
        ? 10.0f : 10.0f + 180.0f * (normalized * 2.0f - 1.0f);
    const float green = normalized <= 0.5f
        ? 60.0f + 155.0f * normalized * 2.0f
        : 215.0f + 40.0f * (normalized * 2.0f - 1.0f);
    matrix.setPixelColor(day,
        static_cast<uint8_t>(level * red / 255.0f + 0.5f),
        static_cast<uint8_t>(level * green / 255.0f + 0.5f),
        level);
  }
  matrix.show();
}

void setup() {
  Serial.begin(115200);
  matrix.begin();
  matrix.setBrightness(MAX_BRIGHTNESS);
  matrix.clear();
  matrix.show();
  delay(500);
  Serial.println("SF NOAA historical-date tide predictions | station 9414290");
  Serial.printf("Dates: %s through %s | 64 LEDs, one day per LED\n",
                TIDE_START_DATE, TIDE_END_DATE);
  Serial.printf("96 samples/day | local SF time | MLLW %.3f to %.3f m\n",
                TIDE_MIN_MM / 1000.0f, TIDE_MAX_MM / 1000.0f);
  Serial.printf("Brightness: %u/255 | GPIO: %u | offline playback | cycle: %.3f s\n",
                MAX_BRIGHTNESS, LED_PIN, FRAME_DELAY_MS * TIDE_SAMPLES_PER_DAY / 1000.0f);
  Serial.println("Mapping: shared tide range, squared intensity (contrast exponent 2)");
  Serial.println("Colors: deep blue -> cyan -> pale cyan-white");
  lastFrameAt = lastRenderAt = millis();
  renderFrame(0.0f);
}

void loop() {
  const uint32_t now = millis();
  if (now - lastFrameAt >= FRAME_DELAY_MS) {
    const uint32_t steps = (now - lastFrameAt) / FRAME_DELAY_MS;
    frame = (frame + steps) % TIDE_SAMPLES_PER_DAY;
    lastFrameAt += steps * FRAME_DELAY_MS;
    if (frame % 4 == 0) {
      Serial.printf("Local tide time: %02u:%02u\n", frame / 4, (frame % 4) * 15);
    }
  }
  if (now - lastRenderAt >= RENDER_INTERVAL_MS) {
    lastRenderAt = now;
    renderFrame((now - lastFrameAt) / static_cast<float>(FRAME_DELAY_MS));
  }
}
