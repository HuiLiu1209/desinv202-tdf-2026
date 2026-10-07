#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>

#include "secrets.h"

// ======================================================
// LED MATRIX
// ======================================================

#define LED_PIN 13
#define LED_COUNT 64

Adafruit_NeoPixel matrix(
  LED_COUNT,
  LED_PIN,
  NEO_GRB + NEO_KHZ800
);

// 你现在还是 ESP32 USB 给 Matrix 供电
// 先锁死在 3 / 255
#define MAX_BRIGHTNESS 3

// 每一帧之间等待多久
// 96 个 frame × 100ms
// 整个“一天”大约 9.6 秒播放完
#define FRAME_DELAY_MS 100


// ======================================================
// DATA SETTINGS
// ======================================================

#define DAYS 64
#define TIMES_PER_DAY 96

// tideData[哪一天][一天中的哪个时间]
//
// tideData[0][0]  = 第1天 00:00
// tideData[0][1]  = 第1天 00:15
// tideData[1][0]  = 第2天 00:00
//
// ...
float tideData[DAYS][TIMES_PER_DAY];

// 如果某一天 API 获取失败
bool dayValid[DAYS];


// ======================================================
// START DATE
// ======================================================

// 第一版 prototype：
// 从 2026-10-05 开始，连续获取 64 天

struct SimpleDate {
  int year;
  int month;
  int day;
};

SimpleDate startDate = {
  2026,
  10,
  5
};


// ======================================================
// GLOBAL TIDE RANGE
// ======================================================

// 后面会扫描全部 64 天
// 找出整体最低潮和最高潮

float globalMinTide = 9999;
float globalMaxTide = -9999;


// ======================================================
// DATE FUNCTIONS
// ======================================================

bool isLeapYear(int year) {

  if (year % 400 == 0) return true;
  if (year % 100 == 0) return false;
  if (year % 4 == 0) return true;

  return false;
}


int daysInMonth(int year, int month) {

  if (
    month == 1 ||
    month == 3 ||
    month == 5 ||
    month == 7 ||
    month == 8 ||
    month == 10 ||
    month == 12
  ) {
    return 31;
  }

  if (
    month == 4 ||
    month == 6 ||
    month == 9 ||
    month == 11
  ) {
    return 30;
  }

  if (month == 2) {

    if (isLeapYear(year)) {
      return 29;
    }

    return 28;
  }

  return 30;
}


void addOneDay(SimpleDate &date) {

  date.day++;

  if (
    date.day >
    daysInMonth(date.year, date.month)
  ) {

    date.day = 1;
    date.month++;

    if (date.month > 12) {

      date.month = 1;
      date.year++;
    }
  }
}


String formatDate(SimpleDate date) {

  char buffer[9];

  sprintf(
    buffer,
    "%04d%02d%02d",
    date.year,
    date.month,
    date.day
  );

  return String(buffer);
}


// ======================================================
// WIFI
// ======================================================

void connectWiFi() {

  Serial.print("Connecting to WiFi");

  WiFi.begin(
    WIFI_SSID,
    WIFI_PASSWORD
  );

  while (
    WiFi.status() != WL_CONNECTED
  ) {

    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected!");

  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}


// ======================================================
// FETCH ONE DAY
// ======================================================

bool fetchOneDay(
  String date,
  int dayIndex
) {

  Serial.println();
  Serial.print("Day ");
  Serial.print(dayIndex + 1);
  Serial.print("/");
  Serial.print(DAYS);
  Serial.print(" | ");
  Serial.println(date);


  // ------------------------------------------
  // Build NOAA URL
  // ------------------------------------------

  String url =
    "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    "?begin_date=" + date +
    "&end_date=" + date +
    "&station=9414290"
    "&product=predictions"
    "&datum=MLLW"
    "&time_zone=lst_ldt"
    "&interval=15"
    "&units=metric"
    "&application=HuiAmbientDisplay"
    "&format=json";


  // ------------------------------------------
  // HTTPS
  // ------------------------------------------

  WiFiClientSecure client;

  // prototype 暂时跳过 certificate verification
  client.setInsecure();

  HTTPClient http;

  http.setTimeout(15000);

  http.begin(client, url);


  // ------------------------------------------
  // GET
  // ------------------------------------------

  int responseCode =
    http.GET();

  Serial.print("HTTP: ");
  Serial.println(responseCode);


  if (responseCode != 200) {

    http.end();

    Serial.println("Request failed.");

    return false;
  }


  // ------------------------------------------
  // Get JSON
  // ------------------------------------------

  String json =
    http.getString();

  http.end();


  // ------------------------------------------
  // Parse JSON
  // ------------------------------------------

  JsonDocument doc;

  DeserializationError error =
    deserializeJson(doc, json);


  if (error) {

    Serial.print("JSON error: ");
    Serial.println(error.c_str());

    return false;
  }


  JsonArray predictions =
    doc["predictions"].as<JsonArray>();


  if (predictions.isNull()) {

    Serial.println("No predictions.");

    return false;
  }


  // ------------------------------------------
  // Temporary raw values
  // ------------------------------------------

  float tempData[128];

  int tempCount = 0;


  for (
    JsonObject prediction :
    predictions
  ) {

    if (tempCount >= 128) {
      break;
    }

    float value =
      prediction["v"].as<float>();

    tempData[tempCount] =
      value;

    tempCount++;
  }


  Serial.print("Points received: ");
  Serial.println(tempCount);


  if (tempCount < 2) {

    Serial.println("Not enough data.");

    return false;
  }


  // ------------------------------------------
  // Convert to exactly 96 points
  //
  // 正常一天：
  // 24 × 4 = 96
  //
  // 这里仍然做一次 resample，
  // 防止某些日期数量不完全一样
  // ------------------------------------------

  for (
    int timeIndex = 0;
    timeIndex < TIMES_PER_DAY;
    timeIndex++
  ) {

    int sourceIndex =
      round(
        timeIndex
        *
        (tempCount - 1)
        /
        95.0
      );


    float value =
      tempData[sourceIndex];


    tideData[dayIndex][timeIndex] =
      value;


    // 顺便计算整个64天共同的 min/max

    if (value < globalMinTide) {
      globalMinTide = value;
    }

    if (value > globalMaxTide) {
      globalMaxTide = value;
    }
  }


  Serial.println("OK");

  return true;
}


// ======================================================
// FETCH ALL 64 DAYS
// ======================================================

void fetchAllDays() {

  SimpleDate currentDate =
    startDate;


  for (
    int day = 0;
    day < DAYS;
    day++
  ) {

    String dateString =
      formatDate(currentDate);


    bool success =
      fetchOneDay(
        dateString,
        day
      );


    dayValid[day] =
      success;


    if (!success) {

      // 如果某天失败
      // 暂时全部设成 0

      for (
        int t = 0;
        t < TIMES_PER_DAY;
        t++
      ) {

        tideData[day][t] = 0;
      }
    }


    // 下一天
    addOneDay(currentDate);


    // 不要连续疯狂请求 NOAA
    delay(200);
  }


  Serial.println();
  Serial.println("======================");
  Serial.println("ALL DATA LOADED");
  Serial.println("======================");

  Serial.print("Global min tide: ");
  Serial.println(globalMinTide);

  Serial.print("Global max tide: ");
  Serial.println(globalMaxTide);
}


// ======================================================
// MAP TIDE → LED
// ======================================================

void renderFrame(int timeIndex) {

  // timeIndex:
  //
  // 0  = 00:00
  // 1  = 00:15
  // 2  = 00:30
  // ...
  // 95 = 23:45


  for (
    int day = 0;
    day < DAYS;
    day++
  ) {

    // 如果某一天 API 失败
    // 对应 LED 关掉

    if (!dayValid[day]) {

      matrix.setPixelColor(
        day,
        matrix.Color(0, 0, 0)
      );

      continue;
    }


    float tide =
      tideData[day][timeIndex];


    // ------------------------------------------
    // Normalize
    //
    // global min → 0
    // global max → 1
    // ------------------------------------------

    float normalized = 0;


    if (
      globalMaxTide >
      globalMinTide
    ) {

      normalized =
        (
          tide -
          globalMinTide
        )
        /
        (
          globalMaxTide -
          globalMinTide
        );
    }


    normalized =
      constrain(
        normalized,
        0.0,
        1.0
      );


    // ------------------------------------------
    // 0-1 → RGB 0-255
    //
    // 实际整体亮度仍然被
    // setBrightness(3)
    // 限制
    // ------------------------------------------

    int brightness =
      round(
        normalized * 255
      );


    // 第一版先全部用白色

    matrix.setPixelColor(
      day,
      matrix.Color(
        brightness,
        brightness,
        brightness
      )
    );
  }


  // 64颗一起更新
  matrix.show();


  // ------------------------------------------
  // Serial Monitor 显示现在模拟几点
  // ------------------------------------------

  int totalMinutes =
    timeIndex * 15;

  int hour =
    totalMinutes / 60;

  int minute =
    totalMinutes % 60;


  Serial.print("Frame ");

  Serial.print(timeIndex);

  Serial.print(" | Time ");

  if (hour < 10) {
    Serial.print("0");
  }

  Serial.print(hour);

  Serial.print(":");

  if (minute < 10) {
    Serial.print("0");
  }

  Serial.println(minute);
}


// ======================================================
// SETUP
// ======================================================

void setup() {

  Serial.begin(115200);

  delay(1000);


  // ------------------------------------------
  // Matrix
  // ------------------------------------------

  matrix.begin();

  matrix.setBrightness(
    MAX_BRIGHTNESS
  );

  matrix.clear();

  matrix.show();


  // ------------------------------------------
  // WiFi
  // ------------------------------------------

  connectWiFi();


  // ------------------------------------------
  // Fetch 64 days
  // ------------------------------------------

  fetchAllDays();


  Serial.println();
  Serial.println("Starting animation...");
}


// ======================================================
// LOOP
// ======================================================

void loop() {

  // =========================================
  // 一天有 96 个 15-minute frame
  // =========================================

  for (
    int timeIndex = 0;
    timeIndex < TIMES_PER_DAY;
    timeIndex++
  ) {

    renderFrame(
      timeIndex
    );

    delay(
      FRAME_DELAY_MS
    );
  }


  // 到 23:45 后
  // 自动重新从 00:00 播放
}