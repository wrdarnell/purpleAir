"""Platform for PurpleAir sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
	SensorDeviceClass,
	SensorEntity,
	SensorStateClass,
)
from homeassistant.const import CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.sensor import (PLATFORM_SCHEMA)

import datetime
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from .purpleAirData import purpleAirData

class PurpleAirMonitoredValue():
	def __init__(self, prefix, name, unit, decimalPlaces, devClass):
		self.prefix        = prefix
		self.name          = name
		self.unit          = unit
		self.decimalPlaces = decimalPlaces
		self.devClass      = devClass

CONFIG_URL    = "url"
CONFIG_VALUES = "monitored_values"
VALUE_TYPES = {
	'pm2_5_atm':  PurpleAirMonitoredValue("pm2_5_atm" , "PM 2.5"           , CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, 1, SensorDeviceClass.PM25),
	'pm10_0_atm': PurpleAirMonitoredValue("pm10_0_atm", "PM 10"            , CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, 1, SensorDeviceClass.PM10),
	'pm2.5_aqi':  PurpleAirMonitoredValue("pm2.5_aqi" , "Air Quality Index", ""                                      , 0, SensorDeviceClass.AQI),	
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
	vol.Required(CONFIG_URL): cv.string,
	vol.Required(CONFIG_VALUES):
		vol.All(cv.ensure_list, vol.Length(min=1), [vol.In(VALUE_TYPES)])
})

def setup_platform(
	hass: HomeAssistant,
	config: ConfigType,
	add_entities: AddEntitiesCallback,
	discovery_info: DiscoveryInfoType | None = None
) -> None:
	"""Set up the sensor platform."""
	url = config[CONFIG_URL]
	entities = []
	paData = purpleAirData(url, 30, config[CONFIG_VALUES])
	for value in config[CONFIG_VALUES]:
		entities.append(PurpleAirEntity(url, VALUE_TYPES[value], paData))
	add_entities(entities)

class PurpleAirEntity(SensorEntity):
	"""Representation of a Sensor."""
	
	def __init__(self, url, valueConfig, paData) -> None:
		self._url                             = url
		self._prefix                          = valueConfig.prefix
		self._attr_name                       = valueConfig.name
		self._attr_native_unit_of_measurement = valueConfig.unit
		self._attr_device_class               = valueConfig.devClass
		self._decimalPlaces                   = valueConfig.decimalPlaces
		self._attr_state_class                = SensorStateClass.MEASUREMENT
		self._paData                          = paData

	def update(self) -> None:
		"""Fetch new state data for the sensor.

		This is the only method that should fetch new data for Home Assistant.
		"""
		value = self._paData.readings[self._prefix]
		if self._decimalPlaces == 0:
			self._attr_native_value = int(value)
		else:
			self._attr_native_value = value
		
	@property
	def unique_id(self):
		return self._prefix
