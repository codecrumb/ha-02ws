# 02WS Weather — Home Assistant Integration

Custom integration for pulling live Jerusalem weather data from [02WS](https://www.02ws.co.il) (JeruSky / ירוש־מים).

It pulls from `https://v2013.02ws.co.il/02wsjson.txt`, the unauthenticated JSON
feed the 02WS website itself renders from (the old `www.02ws.co.il/api/...`
endpoint is dead — it now redirects to a stale path via Cloudflare). No
cookies, session, or special headers are needed; verified 2026-10-29.

## About

- **Domain**: `o2ws` (note: **o**2ws, not 02ws — a HA integration domain is also
  a Python package name, and `02ws` isn't a legal one since it starts with a digit)
- **Display Name**: "02WS Weather" (shown in UI)
- **Update Interval**: 5 minutes
- **Platforms**: Sensor, Binary Sensor

## Installation via HACS

1. Ensure the repository is public.
2. Go to **HACS → Integrations → Custom repositories**
3. Paste this repo URL and select **Integration**
4. Search for **02WS Weather** and install
5. Restart Home Assistant

## Add to `configuration.yaml`

```yaml
sensor:
  - platform: o2ws
binary_sensor:
  - platform: o2ws
```

## Entities

**Sensors** — current conditions: Temperature (x3 probes), Humidity, Pressure,
Wind Direction/Speed, Rain Rate/Chance, Solar Radiation, Dew Point, Wind Chill,
Heat Index, Feels Like, UV Index, PM10, PM2.5. Today's stats: Sunshine Hours,
Rain Total, High/Low Temperature, Sunrise, Sunset. Plus a Clothing
Recommendation sensor from 02WS's own "coldmeter" advice engine.

**Binary sensor**: Weather Alert — on when 02WS has an active or forecast
alert, with the alert text as attributes.
