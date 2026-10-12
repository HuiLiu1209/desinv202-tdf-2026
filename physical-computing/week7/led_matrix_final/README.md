# LED Matrix: Final Stage Version

Arduino sketch for an Adafruit Feather ESP32 V2 and 64 GRB NeoPixels, with DIN connected to GPIO 13. The required Arduino library is Adafruit NeoPixel.

The stage sketch is `led_matrix_final.ino`. The network prototype is retained at `../led_matrix/led_matrix.ino`.

Tide data is prepared on a computer before the performance and uploaded with the program to ESP32 flash memory. This fixed dataset provides consistent playback without Wi-Fi, network delays, or API availability affecting the stage display. The data remains stored after power loss or a restart.

`fetch_tides.py` is a computer-side data preparation tool. It is not uploaded to the ESP32 or run during the performance. A new download and firmware upload are required only when changing the date range.

Dataset: **2026-08-08 through 2026-10-10**, covering 64 complete dates. Source: NOAA San Francisco station **9414290**, with `product=predictions`, `datum=MLLW`, `units=metric`, `time_zone=lst_ldt`, and `interval=15`. These are tide predictions for historical dates, not observed water levels. [NOAA API documentation](https://api.tidesandcurrents.noaa.gov/api/prod/).

## Playback

- Each LED represents one date in physical LED order. LED 0 is the oldest date; LED 63 is the most recent. On a serpentine matrix, dates follow the serpentine wiring.
- All LEDs share the same local playback time, from 00:00 through 23:45. Each date contains 96 fifteen-minute samples, for a total of 6,144 samples.
- Heights are normalized against the minimum and maximum of the entire dataset. Squaring the normalized value dims low tides and emphasizes high tides while retaining comparisons between dates. The global brightness limit is `MAX_BRIGHTNESS = 10` on a 0-255 scale.
- Color changes continuously from deep blue through cyan to pale cyan-white as tide height increases. The blue channel follows the squared intensity curve; red and green determine the hue. Perceived brightness can vary with color.
- Each sample lasts 63 ms, producing a 6.048-second cycle. Interpolated frames render every 20 ms. The final sample is held until playback restarts; the midnight loop boundary may have a visible jump.
- Playback starts from the embedded dataset without Wi-Fi or an API key. Serial output uses 115200 baud.

## Preparing a Different Dataset

Run from the project directory:

```sh
python3 fetch_tides.py --end-date 2026-10-10
```

Without `--end-date`, the last date defaults to yesterday in the San Francisco time zone. The script downloads NOAA predictions, validates all timestamps, sample counts, and values, then generates `tide_data.h` and archives the full response in `noaa_tides.json`. If a daylight-saving transition produces a date with a different sample count, validation fails and the existing dataset is retained.

After preparing a new dataset, compile and upload `led_matrix_final.ino`. Brightness and playback timing are configured by the constants at the top of the sketch.

Board target: `esp32:esp32:adafruit_feather_esp32_v2`. Use **115200** under Arduino IDE's Tools > Upload Speed; this rate completed upload and flash verification on the connected board.
