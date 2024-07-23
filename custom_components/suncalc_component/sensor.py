import logging
import warnings
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
import suncalc
from datetime import datetime
import pandas as pd

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=12)

SENSOR_TYPES = {
    "dawn": "Dawn",
    "sunrise": "Sunrise",
    "solarNoon": "Culmination",
    "sunset": "Sunset",
    "dusk": "Dusk",
    "daylight_duration": "Daylight Duration"
}

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the sensor platform."""
    latitude = hass.config.latitude
    longitude = hass.config.longitude
    async_add_entities([
        SunCalcSensor(latitude, longitude, sensor_type)
        for sensor_type in SENSOR_TYPES
    ])

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up SunCalc sensor from a config entry."""
    latitude = entry.data[CONF_LATITUDE]
    longitude = entry.data[CONF_LONGITUDE]
    async_add_entities([
        SunCalcSensor(latitude, longitude, sensor_type)
        for sensor_type in SENSOR_TYPES
    ])

class SunCalcSensor(SensorEntity):
    """Representation of a SunCalc Sensor."""

    def __init__(self, latitude, longitude, sensor_type):
        """Initialize the sensor."""
        self._latitude = latitude
        self._longitude = longitude
        self._sensor_type = sensor_type
        self._name = SENSOR_TYPES[sensor_type]
        self._unique_id = f"{latitude}-{longitude}-{sensor_type}"
        self._state = None
        self._attributes = {}
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return f'SunCalc {self._name} Sensor'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    def update(self):
        """Fetch new state data for the sensor."""
        try:
            if not (-90 <= self._latitude <= 90):
                raise ValueError(f"Invalid latitude value: {self._latitude}")
            if not (-180 <= self._longitude <= 180):
                raise ValueError(f"Invalid longitude value: {self._longitude}")

            with warnings.catch_warnings():
                warnings.filterwarnings('error', category=RuntimeWarning)
                times = suncalc.get_times(datetime.now(), self._latitude, self._longitude)
                time_value = times.get(self._sensor_type, pd.NaT)
                if pd.isna(time_value):
                    self._state = None
                    _LOGGER.warning(f"SunCalc returned NaT for {self._name}")
                elif self._sensor_type == "daylight_duration":
                    self._state = str(times['sunset'] - times['sunrise'])
                else:
                    self._state = time_value.strftime('%H:%M:%S')
                
                self._attributes.update({
                    "latitude": self._latitude,
                    "longitude": self._longitude
                })
        except RuntimeWarning as rw:
            _LOGGER.warning(f"RuntimeWarning encountered: {rw}")
        except ValueError as ve:
            _LOGGER.error(f"ValueError: {ve}")
        except Exception as e:
            _LOGGER.error(f"Error updating SunCalc sensor {self._name}: {e}")
