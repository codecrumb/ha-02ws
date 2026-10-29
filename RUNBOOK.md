# RUNBOOK — ha-02ws

## Current API: https://v2013.02ws.co.il/02wsjson.txt
## Clothing API: https://v2013.02ws.co.il/coldmeter_service.php?lang=1&json=1&cloth_type=e
## (Old API https://www.02ws.co.il/api/now/0/1/C/1 is dead — Cloudflare 302s it
##  to a stale path. The site rebuilt as a React app; the above subdomain is
##  what it actually fetches from. No auth/cookies needed. Verified 2026-10-29.)
## Both endpoints return content-type text/plain or text/html, NOT
## application/json — must call `resp.json(content_type=None)` in aiohttp or
## it raises ContentTypeError.
## Backup branch: backup-main
## Domain: o2ws (internal), Display: 02WS Weather

### Quick install (one-shot)
1. Push these files to `main`.
2. In Home Assistant: HACS → Integrations → Custom repositories → add repo URL as "Integration".
3. Install integration, restart HA.

### Debug
- If HACS errors `No manifest.json found 'manifest.json'`:
  - Ensure `hacs.json` exists at repo ROOT (not in custom_components/) with proper configuration.
  - Ensure `custom_components/o2ws/manifest.json` exists and is valid JSON.
  - Verify `custom_components/o2ws/` directory exists (not `02ws`).
  - Remove integration from HACS and re-add repo.

### Structure
```
ha-02ws/
├── hacs.json                          # HACS config at ROOT
├── README.md                          # Documentation
└── custom_components/
    └── o2ws/                          # Integration directory (domain name)
        ├── __init__.py
        ├── manifest.json
        ├── const.py
        ├── sensor.py
        └── binary_sensor.py
```

### Key Points
- Domain is `o2ws` (not `02ws`) to comply with Python/HA naming rules
- Display name remains "02WS Weather" for users
- `hacs.json` must be at repository root, not in custom_components/
- The init file MUST be named `__init__.py` (double underscore each side). It
  was previously misnamed `_init__.py` (single leading underscore) — HA's
  component loader needs the real dunder name to import the package at all,
  so that typo alone likely broke the whole integration independent of the
  API being dead. Fixed 2026-10-29.
