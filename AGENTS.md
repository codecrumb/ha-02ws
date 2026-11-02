# AGENTS.md — ha-02ws

Project-specific context for any coding agent (or human) working on this
repo. Read this before making changes — it replaces a separate RUNBOOK and
the external second-brain notes that used to live outside the repo.

## What this is

HACS custom integration pulling 02WS/JeruSky (Jerusalem weather) data into
Home Assistant as sensors + a binary sensor.

## Facts (verified 2026-10-29)

- Current data endpoint: `https://v2013.02ws.co.il/02wsjson.txt`
- Clothing recommendation endpoint:
  `https://v2013.02ws.co.il/coldmeter_service.php?lang=1&json=1&cloth_type=e`
- Both are unauthenticated — no cookies/session/UA/referer needed, confirmed
  across multiple fresh `curl` processes (all HTTP 200). `02wsjson.txt` has
  `access-control-allow-origin: *` and its `last-modified` ticks roughly
  every ~1 minute (faster than the integration's 5-minute poll).
- The OLD endpoint `https://www.02ws.co.il/api/now/0/1/C/1` is dead —
  Cloudflare 302s it to `https://v2013.02ws.co.il/Services.php?...`, which
  itself returns an empty body to a plain curl. Never pursued further since
  `02wsjson.txt` works directly.
- Found the real endpoints by running headless Chromium with
  `--log-net-log=... --net-log-capture-mode=Everything` against
  `https://www.02ws.co.il/` and grepping the NetLog JSON for `02ws.co.il`
  URLs — a lot of ad-tech noise to filter past (Google ads, Criteo,
  IntentIQ, Kueez, etc).
- Domain is `o2ws`, not `02ws`, **on purpose**: an HA integration domain is
  also a Python package name (`custom_components.<domain>`), and `02ws`
  isn't a legal Python identifier (starts with a digit). The display name
  "02WS Weather" is what users actually see.
- Backup branch `backup-main` exists on the remote — leave it alone unless
  asked.

## Gotchas

- Both endpoints serve `content-type: text/plain` / `text/html`, NOT
  `application/json` — aiohttp's `resp.json()` raises `ContentTypeError`
  unless called as `resp.json(content_type=None)`.
- The init file MUST be named `__init__.py` (double underscore each side).
  It was previously misnamed `_init__.py` (single leading underscore) — HA's
  component loader needs the literal dunder name to import the package at
  all, so that typo alone broke the integration independent of the API
  being dead. Fixed 2026-10-29.
- `hacs.json` must live at the repo ROOT, not inside `custom_components/`.
- If HACS errors `No manifest.json found 'manifest.json'`: check
  `custom_components/o2ws/manifest.json` exists and is valid JSON, verify
  the directory is named `o2ws` (not `02ws`), then remove + re-add the repo
  in HACS.

## Decisions

- 2026-10-29: Rewrote `const.py`/`sensor.py`, added `binary_sensor.py` to
  point at the new endpoints and expand sensor coverage ("full expansion"
  was chosen over "fix only" / "fix + air quality"):
  - Current-conditions sensors: temp/temp2/temp3, hum, pressure, winddir,
    windspd, rainrate, rainchance, solarradiation (existing) + dew point,
    wind chill, heat index, feels-like (thw), UV index, PM10, PM2.5 (new).
  - Today sensors: sunshinehours, rain total (existing) + high/low temp,
    sunrise, sunset (new).
  - New `ClothingSensor` from the coldmeter endpoint.
  - New `binary_sensor.o2ws_weather_alert`, on when 02WS has an active or
    forecast alert (`Messages.latestalert0` non-empty or `Messages.alerts`
    non-empty); alert text decoded with `urllib.parse.unquote_plus` (the
    API returns `title0`/`desc0` percent/plus-encoded).
  - Deliberately skipped: hourly/multi-day forecast, activity
    recommendations, user photos, forum dump, moon phase, ads — all present
    in the payload but out of scope for this pass.
  - Added stable `unique_id` per entity (none existed before).
  - Left the 5-minute poll interval alone — data refreshes faster
    server-side but no reason to hammer it more often.
- 2026-10-29: Added MIT `LICENSE` (required for eventual HACS default-store
  submission; not needed for custom-repository installs).
- 2026-11-02: Rewrote from the legacy YAML `async_setup_platform` pattern to
  config entries, so install is "Add Integration" in the UI with no
  `configuration.yaml` editing:
  - `config_flow.py` — single confirm-only step (no fields to ask for:
    no API key, no location). Uses `async_set_unique_id(DOMAIN)` +
    `_abort_if_unique_id_configured()` to block a second instance.
  - `coordinator.py` — `O2wsDataUpdateCoordinator(DataUpdateCoordinator)`,
    one shared fetch of both endpoints per 5-minute interval instead of
    `sensor.py` and `binary_sensor.py` each independently polling. Uses
    `async_get_clientsession(hass)` instead of opening a new
    `aiohttp.ClientSession` per fetch.
  - `device.py` — shared `DeviceInfo` so all entities group under one
    "02WS Weather" device in the UI.
  - `__init__.py` now has `async_setup_entry`/`async_unload_entry` instead
    of the no-op `async_setup`.
  - `sensor.py`/`binary_sensor.py` switched to `async_setup_entry` +
    `CoordinatorEntity` subclasses; field-mapping logic (`SENSOR_DEFINITIONS`,
    alert detection/decoding) is unchanged from the YAML version.
  - `manifest.json`: added `"config_flow": true`.
  - Added `strings.json` + `translations/en.json` for the confirm step's
    title/description text.

## Publishing to HACS

Two different things:

1. **Custom repository** (works today): in HA, HACS → Integrations →
   Custom repositories → add this repo URL as "Integration". Reads
   `hacs.json` + `manifest.json` directly from the branch — no release
   needed.
2. **Official default store** (not done yet): needs a PR to `hacs/default`
   adding this repo. Status: ✅ public repo, ✅ LICENSE, ❌ no tagged GitHub
   Release yet, ❌ no `.github/workflows/` HACS validation action yet. See
   https://hacs.xyz/docs/publish/integration.

## State / next steps

- Earlier (pre-config-entry) version was pushed and is live on
  `origin/main`; user added GitHub topics (`home-assistant`, `hacs`,
  `hacs-integration`, `home-assistant-integration`, `weather`, `jerusalem`)
  and was about to test the custom-repository install in HA.
- The 2026-11-02 config-entry rewrite above is done locally but **not yet
  committed or pushed** — don't push without being asked, same as before.
- Still not tested against a running HA instance (no local HA install in
  this repo) — user will test via HACS custom repository.
- If something's off after testing: re-check `sensor.py`/`binary_sensor.py`
  field paths against a fresh `curl https://v2013.02ws.co.il/02wsjson.txt`
  dump — the site is unversioned and fields could shift.

## Structure

```
ha-02ws/
├── LICENSE
├── README.md                          # user-facing docs
├── AGENTS.md                          # this file — agent/dev context
├── hacs.json                          # HACS config, must be at repo ROOT
└── custom_components/
    └── o2ws/                          # integration dir == domain name
        ├── __init__.py                # async_setup_entry/async_unload_entry
        ├── manifest.json
        ├── const.py
        ├── config_flow.py             # confirm-only setup step
        ├── coordinator.py             # shared DataUpdateCoordinator
        ├── device.py                  # shared DeviceInfo
        ├── sensor.py
        ├── binary_sensor.py
        ├── strings.json
        └── translations/
            └── en.json
```
