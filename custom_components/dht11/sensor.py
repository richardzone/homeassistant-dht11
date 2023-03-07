"""Platform for sensor integration."""
import logging
import os

import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import (
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required("pin"): cv.positive_int,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(
            CONF_TEMPERATURE_UNIT, default=TEMP_CELSIUS
        ): vol.In([TEMP_CELSIUS, TEMP_FAHRENHEIT]),
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the DHT11 sensor."""
    name = config.get(CONF_NAME)
    pin = config["pin"]
    temperature_unit = config[CONF_TEMPERATURE_UNIT]

    try:
        import Adafruit_DHT
    except ImportError:
        _LOGGER.error(
            "Error importing Adafruit_DHT. "
            "Please install the Adafruit Python DHT library."
        )
        return

    def update_dht11():
        """Update the sensor."""
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, pin)
        if temperature is None or humidity is None:
            _LOGGER.warning(
                "Failed to read data from DHT11 sensor on pin %s", pin
            )
            return
        if temperature_unit == TEMP_FAHRENHEIT:
            temperature = temperature * 1.8 + 32
        return temperature, humidity

    add_entities([DHT11Sensor(name, update_dht11)], True)


class DHT11Sensor(SensorEntity):
    """Representation of a DHT11 sensor."""

    def __init__(self, name, update_method):
        """Initialize the sensor."""
        self._name = name
        self._update_method = update_method
        self._state = None
        self._unit_of_measurement = None

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
        """Return the unit of measurement of this entity."""
        return self._unit_of_measurement

    def update(self):
        """Update the sensor."""
        result = self._update_method()
        if result is not None:
            temperature, humidity = result
            self._state = temperature
            self._unit_of_measurement = (
                TEMP_FAHRENHEIT if self.hass.config.units.is_unit("imperial") else TEMP_CELSIUS
            )
        else:
            self._state = None
            self._unit_of_measurement = None
