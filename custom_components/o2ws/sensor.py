import aiohttp
import async_timeout
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.util import Throttle
from .const import BASE_URL, COLDMETER_URL

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)

# key -> (section, field in that section, display name, unit, device class)
# "current" and "today" are the two sections of the 02wsjson.txt payload we pull from.
SENSOR_DEFINITIONS = {
    "temp": ("current", "temp", "Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
    "temp2": ("current", "temp2", "Temperature 2", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
    "temp3": ("current", "temp3", "Temperature 3", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
    "hum": ("current", "hum", "Humidity", PERCENTAGE, SensorDeviceClass.HUMIDITY),
    "pressure": ("current", "pressure", "Pressure", UnitOfPressure.HPA, SensorDeviceClass.PRESSURE),
    "winddir": ("current", "winddir", "Wind Direction", None, None),
    "windspd": ("current", "windspd", "Wind Speed", UnitOfSpeed.KILOMETERS_PER_HOUR, SensorDeviceClass.WIND_SPEED),
    "rainrate": ("current", "rainrate", "Rain Rate", "mm/h", None),
    "rainchance": ("current", "rainchance", "Rain Chance", PERCENTAGE, None),
    "solarradiation": ("current", "solarradiation", "Solar Radiation", "W/m²", SensorDeviceClass.IRRADIANCE),
    "dew": ("current", "dew", "Dew Point", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
    "windchill": ("current", "windchill", "Wind Chill", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
    "heatidx": ("current", "heatidx", "Heat Index", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
    "thw": ("current", "thw", "Feels Like", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
    "uv": ("current", "uv", "UV Index", None, None),
    "pm10": ("current", "pm10", "PM10", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, SensorDeviceClass.PM10),
    "pm25": ("current", "pm25", "PM2.5", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, SensorDeviceClass.PM25),
    "sunshinehours": ("today", "sunshinehours", "Sunshine Hours", "h", None),
    "rain": ("today", "rain", "Rain Total", "mm", None),
    "hightemp": ("today", "hightemp", "Today High Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
    "lowtemp": ("today", "lowtemp", "Today Low Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
    "sunrise": ("today", "sunrise", "Sunrise", None, None),
    "sunset": ("today", "sunset", "Sunset", None, None),
}


async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    data = WeatherData(hass)
    await data.update()

    sensors = [
        WeatherSensor(data, key, section, field, name, unit, device_class)
        for key, (section, field, name, unit, device_class) in SENSOR_DEFINITIONS.items()
    ]
    sensors.append(ClothingSensor(data))

    add_entities(sensors, True)


class WeatherData:
    """Fetches and caches the 02WS JSON payloads shared by all sensors."""

    def __init__(self, hass):
        self.hass = hass
        self.current = {}
        self.today = {}
        self.coldmeter = {}

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def update(self):
        async with aiohttp.ClientSession() as session:
            async with async_timeout.timeout(10):
                async with session.get(BASE_URL) as resp:
                    # served as text/plain, not application/json
                    payload = await resp.json(content_type=None)
            async with async_timeout.timeout(10):
                async with session.get(COLDMETER_URL) as resp:
                    coldmeter_payload = await resp.json(content_type=None)

        jws = payload.get("jws", {})
        self.current = jws.get("current", {})
        self.today = jws.get("today", {})
        self.coldmeter = coldmeter_payload.get("coldmeter", {})


class WeatherSensor(SensorEntity):
    def __init__(self, data, key, section, field, name, unit, device_class):
        self.data = data
        self.key = key
        self._section = section
        self._field = field
        self._name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class

    @property
    def unique_id(self):
        return f"o2ws_{self.key}"

    @property
    def name(self):
        return f"02WS {self._name}"

    @property
    def native_value(self):
        section = self.data.current if self._section == "current" else self.data.today
        return section.get(self._field)

    async def async_update(self):
        await self.data.update()


class ClothingSensor(SensorEntity):
    """What to wear, from 02WS's own coldmeter recommendation engine."""

    def __init__(self, data):
        self.data = data

    @property
    def unique_id(self):
        return "o2ws_clothing"

    @property
    def name(self):
        return "02WS Clothing Recommendation"

    @property
    def native_value(self):
        return self.data.coldmeter.get("clothtitle")

    @property
    def extra_state_attributes(self):
        return {
            "feeling": self.data.coldmeter.get("current_feeling"),
            "cloth_icon": self.data.coldmeter.get("cloth_name"),
        }

    async def async_update(self):
        await self.data.update()
