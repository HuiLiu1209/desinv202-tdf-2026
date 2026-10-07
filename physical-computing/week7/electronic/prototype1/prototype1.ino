#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>
#include <math.h>
#include <stdlib.h>

// 在本 sketch 文件夹中创建本地 secrets.h，定义 WIFI_SSID 和 WIFI_PASSWORD。
// secrets.h 已被 .gitignore 排除；不把真实 WiFi 信息写进这个文件。
#include "secrets.h"

const int LED_PIN = 13;
const int LED_COUNT = 64;
const int MAX_BRIGHTNESS = 3;
const unsigned long WIFI_TIMEOUT_MS = 20000;

// Prototype 1：一天中的时间 → LED 位置，潮位 → 白光亮度。
// 沿用 Prototype 2 的站点和日期，以便比较两种映射方式。
const char* TIDE_DATE = "20261005";
const char* STATION_ID = "9414290";

Adafruit_NeoPixel matrix(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

bool connectWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long startedAt = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - startedAt >= WIFI_TIMEOUT_MS) {
      Serial.println("\nWiFi connection timed out.");
      return false;
    }
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected!");
  return true;
}

bool fetchAndDisplayOneDay() {
  String url =
    String("https://api.tidesandcurrents.noaa.gov/api/prod/datagetter") +
    "?begin_date=" + TIDE_DATE +
    "&end_date=" + TIDE_DATE +
    "&station=" + STATION_ID +
    "&product=predictions"
    "&datum=MLLW"
    "&time_zone=lst_ldt"
    "&interval=15"
    "&units=metric"
    "&application=HuiAmbientDisplay"
    "&format=json";

  Serial.println(url);

  WiFiClientSecure client;
  // 与现有 Prototype 2 一致：原型阶段跳过证书验证。
  client.setInsecure();

  HTTPClient http;
  http.setTimeout(15000);
  if (!http.begin(client, url)) {
    Serial.println("Could not start HTTP request.");
    return false;
  }

  int responseCode = http.GET();
  Serial.print("HTTP: ");
  Serial.println(responseCode);
  if (responseCode != 200) {
    http.end();
    return false;
  }

  String json = http.getString();
  http.end();

  // 使用 ArduinoJson 7，与现有 Prototype 2 的 JsonDocument 写法一致。
  JsonDocument doc;
  DeserializationError error = deserializeJson(doc, json);
  if (error) {
    Serial.print("JSON error: ");
    Serial.println(error.c_str());
    return false;
  }

  if (!doc["error"].isNull()) {
    Serial.print("NOAA error: ");
    Serial.println(doc["error"]["message"].as<const char*>());
    return false;
  }

  JsonArray predictions = doc["predictions"].as<JsonArray>();
  int pointCount = predictions.size();
  if (pointCount < 2) {
    Serial.println("Not enough tide predictions.");
    return false;
  }

  // NOAA 的 v 是字符串。先检查数值，再找当天所有采样点的 min/max。
  float minTide = INFINITY;
  float maxTide = -INFINITY;
  for (JsonObject prediction : predictions) {
    const char* valueText = prediction["v"].as<const char*>();
    const char* timeText = prediction["t"].as<const char*>();
    if (valueText == nullptr || timeText == nullptr) {
      Serial.println("Missing tide value or timestamp.");
      return false;
    }

    char* valueEnd;
    float tide = strtof(valueText, &valueEnd);
    if (valueEnd == valueText || *valueEnd != '\0' || !isfinite(tide)) {
      Serial.println("Invalid tide value.");
      return false;
    }

    if (tide < minTide) minTide = tide;
    if (tide > maxTide) maxTide = tide;
  }

  Serial.print("Points received: ");
  Serial.println(pointCount);
  Serial.print("Min / max tide (m): ");
  Serial.print(minTide, 3);
  Serial.print(" / ");
  Serial.println(maxTide, 3);

  matrix.clear();
  for (int led = 0; led < LED_COUNT; led++) {
    // 通常一天有 96 个点。均匀选取 64 个，保留首尾时间点。
    // LED 0 → 00:00，LED 63 → 23:45；位置沿 Matrix 的蛇形编号排列。
    int sourceIndex = roundf(led * (pointCount - 1) / float(LED_COUNT - 1));
    JsonObject prediction = predictions[sourceIndex].as<JsonObject>();
    float tide = prediction["v"].as<float>();

    float normalized = 0;
    if (maxTide > minTide) {
      normalized = (tide - minTide) / (maxTide - minTide);
    }
    normalized = constrain(normalized, 0.0f, 1.0f);

    // 最低潮 → 0，最高潮 → 255；整体亮度仍限制为 3/255。
    int brightness = roundf(normalized * 255);
    matrix.setPixelColor(led, matrix.Color(brightness, brightness, brightness));

    Serial.print("LED ");
    Serial.print(led);
    Serial.print(" | ");
    Serial.print(prediction["t"].as<const char*>());
    Serial.print(" | tide (m): ");
    Serial.print(tide, 3);
    Serial.print(" | brightness: ");
    Serial.println(brightness);
  }

  matrix.show();
  Serial.println("Prototype 1 displayed. The image stays static until reset.");
  return true;
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  matrix.begin();
  matrix.setBrightness(MAX_BRIGHTNESS);
  matrix.clear();
  matrix.show();

  if (!connectWiFi() || !fetchAndDisplayOneDay()) {
    Serial.println("Prototype 1 failed. Check Serial Monitor, then reset to retry.");
  }
}

void loop() {
  // 不推进时间、不重新请求数据：64 颗灯同时呈现同一天的静态潮位分布。
  delay(1000);
}
