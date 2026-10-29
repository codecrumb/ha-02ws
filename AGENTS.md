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

- Code rewritten and compiles clean (`python3 -m py_compile`), not yet
  tested against a running HA instance (no local HA install in this repo).
- Commits exist locally but are intentionally unpushed until testing is
  done via custom-repository install — don't push without being asked.
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
        ├── __init__.py
        ├── manifest.json
        ├── const.py
        ├── sensor.py
        └── binary_sensor.py
```
