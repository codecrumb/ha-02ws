import aiohttp
import async_timeout
from datetime import timedelta
from urllib.parse import unquote_plus
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.util import Throttle
from .const import BASE_URL

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)


async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    data = AlertData(hass)
    await data.update()
    add_entities([WeatherAlertSensor(data)], True)


class AlertData:
    def __init__(self, hass):
        self.hass = hass
        self.messages = {}
        self.alerts = []

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def update(self):
        async with aiohttp.ClientSession() as session:
            async with async_timeout.timeout(10):
                async with session.get(BASE_URL) as resp:
                    # served as text/plain, not application/json
                    payload = await resp.json(content_type=None)

        jws = payload.get("jws", {})
        self.messages = jws.get("Messages", {})
        self.alerts = self.messages.get("alerts", [])


class WeatherAlertSensor(BinarySensorEntity):
    """On when 02WS has an active or forecast weather alert."""

    def __init__(self, data):
        self.data = data

    @property
    def unique_id(self):
        return "o2ws_weather_alert"

    @property
    def name(self):
        return "02WS Weather Alert"

    @property
    def device_class(self):
        return BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self):
        latest = self.data.messages.get("latestalert0", "")
        return bool(latest.strip()) or len(self.data.alerts) > 0

    @property
    def extra_state_attributes(self):
        alerts = [
            {
                "title": unquote_plus(alert.get("title0", "")),
                "description": unquote_plus(alert.get("desc0", "")),
                "type": alert.get("type"),
            }
            for alert in self.data.alerts
        ]
        return {
            "title": unquote_plus(self.data.messages.get("latestalert0", "")),
            "description": unquote_plus(self.data.messages.get("latestalert1", "")),
            "forecast_alerts": alerts,
        }

    async def async_update(self):
        await self.data.update()
