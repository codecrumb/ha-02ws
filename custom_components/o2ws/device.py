from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

DEVICE_INFO = DeviceInfo(
    identifiers={(DOMAIN, DOMAIN)},
    name="02WS Weather",
    manufacturer="02WS / JeruSky",
    model="Jerusalem weather feed",
)
