from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .device import DEVICE_INFO

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


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        WeatherSensor(coordinator, key, section, field, name, unit, device_class)
        for key, (section, field, name, unit, device_class) in SENSOR_DEFINITIONS.items()
    ]
    sensors.append(ClothingSensor(coordinator))

    async_add_entities(sensors)


class WeatherSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, section, field, name, unit, device_class):
        super().__init__(coordinator)
        self._section = section
        self._field = field
        self._attr_unique_id = f"o2ws_{key}"
        self._attr_name = f"02WS {name}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_device_info = DEVICE_INFO

    @property
    def native_value(self):
        return self.coordinator.data[self._section].get(self._field)


class ClothingSensor(CoordinatorEntity, SensorEntity):
    """What to wear, from 02WS's own coldmeter recommendation engine."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = "o2ws_clothing"
        self._attr_name = "02WS Clothing Recommendation"
        self._attr_device_info = DEVICE_INFO

    @property
    def native_value(self):
        return self.coordinator.data["coldmeter"].get("clothtitle")

    @property
    def extra_state_attributes(self):
        coldmeter = self.coordinator.data["coldmeter"]
        return {
            "feeling": coldmeter.get("current_feeling"),
            "cloth_icon": coldmeter.get("cloth_name"),
        }
