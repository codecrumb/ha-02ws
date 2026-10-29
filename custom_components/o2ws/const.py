DOMAIN = "o2ws"

# The original https://www.02ws.co.il/api/now/... endpoint is dead (302s to a
# stale path). The site now serves live data from this subdomain instead,
# unauthenticated and CORS-open (access-control-allow-origin: *), refreshed
# roughly every minute. Verified 2026-10-29.
BASE_URL = "https://v2013.02ws.co.il/02wsjson.txt"
COLDMETER_URL = (
    "https://v2013.02ws.co.il/coldmeter_service.php?lang=1&json=1&cloth_type=e"
)
