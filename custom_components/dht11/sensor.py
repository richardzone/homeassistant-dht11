"""
Home Assistant Integration for DHT11 temperature and humidity sensor.
"""
import logging
import voluptuous as vol
import adafruit_dht
import board
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    TEMP_CELSIUS,
    UNIT_PERCENTAGE,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity

DEFAULT_NAME = "DHT11 Sensor"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_TEMPERATURE_UNIT, default=TEMP_CELSIUS): vol.Any(
            TEMP_CELSIUS, "F"
        ),
    }
)

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the DHT11 sensor."""
    name = config[CONF_NAME]
    temperature_unit = config[CONF_TEMPERATURE_UNIT]

    # Detect GPIO pin connected to DHT11 sensor
    dht_device = adafruit_dht.DHT11(board.GENERAL_PURPOSE)

    sensor = DHT11Sensor(dht_device, name, temperature_unit)
    add_entities([sensor])


class DHT11Sensor(Entity):
    """Representation of a DHT11 sensor."""

    def __init__(self, dht_device, name, temperature_unit):
        """Initialize the sensor."""
        self._name = name
        self._temperature_unit = temperature_unit
        self._state = None
        self._humidity = None
        self._temperature = None
        self._dht_device = dht_device

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        if self._temperature_unit == "F":
            return self._temperature_unit
        return TEMP_CELSIUS

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {"humidity": self._humidity, "temperature": self._temperature}

    @property
    def available(self):
        """Return if entity is available."""
        return self._state is not None

    def update(self):
        """Get the latest data from the sensor."""
        try:
            temperature_celsius = self._dht_device.temperature
            humidity_percent = self._dht_device.humidity
            if temperature_celsius is not None and humidity_percent is not None:
                if self._temperature_unit == "F":
                    temperature_fahrenheit = temperature_celsius * 1.8 + 32.0
                    self._state = temperature_fahrenheit
                else:
                    self._state = temperature_celsius
                self._humidity = humidity_percent
                self._temperature = temperature_celsius
                _LOGGER.debug(
                    "Temperature: %s %s, Humidity: %s %s",
                    self._temperature,
                    self.unit_of_measurement,
                    self._humidity,
                    UNIT_PERCENTAGE,
                )
        except Exception as ex:
            _LOGGER.error("Error updating DHT11 sensor data: %s", ex)
            self._state = None
            self._humidity = None
            self._temperature = None
