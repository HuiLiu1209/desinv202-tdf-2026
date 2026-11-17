#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>

#include "secrets.h"

// 64-pixel GRB NeoPixel matrix connected to GPIO 13.

#define LED_PIN 13
#define LED_COUNT 64

Adafruit_NeoPixel matrix(
  LED_COUNT,
  LED_PIN,
  NEO_GRB + NEO_KHZ800
);

// Brightness limit for the USB-powered prototype, on a 0-255 scale.
#define MAX_BRIGHTNESS 3

// 96 frames at 100 ms per frame produce a 9.6-second playback cycle.
#define FRAME_DELAY_MS 100


// One day per LED, with 96 fifteen-minute samples per day.

#define DAYS 64
#define TIMES_PER_DAY 96

// tideData[day][time slot]: slot 0 is 00:00, slot 1 is 00:15.
float tideData[DAYS][TIMES_PER_DAY];

// A day is valid only when its API response has been loaded successfully.
bool dayValid[DAYS];


// First date of the prototype's 64-day NOAA prediction request.

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


// Shared extrema normalize tide heights across all successfully loaded days.

float globalMinTide = 9999;
float globalMaxTide = -9999;


// Gregorian calendar helpers for advancing the API request date.

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


// Load one date of NOAA predictions into the corresponding LED's data row.

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


  // San Francisco station: 15-minute predictions in meters relative to MLLW.

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


  WiFiClientSecure client;

  // Certificate verification is disabled in this network prototype.
  client.setInsecure();

  HTTPClient http;

  http.setTimeout(15000);

  http.begin(client, url);


  int responseCode =
    http.GET();

  Serial.print("HTTP: ");
  Serial.println(responseCode);


  if (responseCode != 200) {

    http.end();

    Serial.println("Request failed.");

    return false;
  }


  String json =
    http.getString();

  http.end();


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


  // Buffer up to 128 API values before resampling.

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


  // Resample by nearest source index to fill 96 daily slots.
  // API responses with different sample counts use the same playback length.

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


    // Update the tide range shared by all 64 dates.

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


// Complete all daily API requests before starting playback.

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

      // Clear failed rows; dayValid keeps the associated LED off during playback.

      for (
        int t = 0;
        t < TIMES_PER_DAY;
        t++
      ) {

        tideData[day][t] = 0;
      }
    }


    addOneDay(currentDate);


    // Space API requests by 200 ms to reduce the request rate.
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


// Each LED displays one date at the same local time as the other LEDs.

void renderFrame(int timeIndex) {

  // Fifteen-minute local time slots: 0 = 00:00, 95 = 23:45.


  for (
    int day = 0;
    day < DAYS;
    day++
  ) {

    // Failed API requests are displayed as unlit LEDs.

    if (!dayValid[day]) {

      matrix.setPixelColor(
        day,
        matrix.Color(0, 0, 0)
      );

      continue;
    }


    float tide =
      tideData[day][timeIndex];


    // Normalize against the shared range: minimum = 0, maximum = 1.

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


    // Convert to an 8-bit color level; setBrightness applies the global limit.

    int brightness =
      round(
        normalized * 255
      );


    // Equal red, green, and blue values produce white light.

    matrix.setPixelColor(
      day,
      matrix.Color(
        brightness,
        brightness,
        brightness
      )
    );
  }


  matrix.show();


  // Report the local tide time represented by the active frame.

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


void setup() {

  Serial.begin(115200);

  delay(1000);


  matrix.begin();

  matrix.setBrightness(
    MAX_BRIGHTNESS
  );

  matrix.clear();

  matrix.show();


  connectWiFi();


  fetchAllDays();


  Serial.println();
  Serial.println("Starting animation...");
}


void loop() {

  // Play all 96 daily slots, then restart at 00:00 after the 23:45 frame.

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


}
