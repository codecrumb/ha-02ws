from urllib.parse import unquote_plus

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .device import DEVICE_INFO


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WeatherAlertSensor(coordinator)])


class WeatherAlertSensor(CoordinatorEntity, BinarySensorEntity):
    """On when 02WS has an active or forecast weather alert."""

    _attr_unique_id = "o2ws_weather_alert"
    _attr_name = "02WS Weather Alert"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_device_info = DEVICE_INFO

    @property
    def is_on(self):
        messages = self.coordinator.data["messages"]
        latest = messages.get("latestalert0", "")
        return bool(latest.strip()) or len(messages.get("alerts", [])) > 0

    @property
    def extra_state_attributes(self):
        messages = self.coordinator.data["messages"]
        alerts = [
            {
                "title": unquote_plus(alert.get("title0", "")),
                "description": unquote_plus(alert.get("desc0", "")),
                "type": alert.get("type"),
            }
            for alert in messages.get("alerts", [])
        ]
        return {
            "title": unquote_plus(messages.get("latestalert0", "")),
            "description": unquote_plus(messages.get("latestalert1", "")),
            "forecast_alerts": alerts,
        }
