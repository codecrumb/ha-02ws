import logging
from datetime import timedelta

import async_timeout
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import BASE_URL, COLDMETER_URL

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=5)


class O2wsDataUpdateCoordinator(DataUpdateCoordinator):
    """Fetches the 02WS JSON payloads once per interval, shared by all platforms."""

    def __init__(self, hass):
        super().__init__(
            hass,
            _LOGGER,
            name="o2ws",
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        session = async_get_clientsession(self.hass)
        try:
            async with async_timeout.timeout(10):
                async with session.get(BASE_URL) as resp:
                    # served as text/plain, not application/json
                    payload = await resp.json(content_type=None)
            async with async_timeout.timeout(10):
                async with session.get(COLDMETER_URL) as resp:
                    coldmeter_payload = await resp.json(content_type=None)
        except Exception as err:
            raise UpdateFailed(f"Error fetching 02WS data: {err}") from err

        jws = payload.get("jws", {})
        return {
            "current": jws.get("current", {}),
            "today": jws.get("today", {}),
            "messages": jws.get("Messages", {}),
            "coldmeter": coldmeter_payload.get("coldmeter", {}),
        }
