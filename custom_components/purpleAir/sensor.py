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

import datetime
import requests

def setup_platform(
	hass: HomeAssistant,
	config: ConfigType,
	add_entities: AddEntitiesCallback,
	discovery_info: DiscoveryInfoType | None = None
) -> None:
	"""Set up the sensor platform."""
	add_entities([PurpleAirSensor()])


class PurpleAirSensor(SensorEntity):
	"""Representation of a Sensor."""

	_attr_name = "PM 2.5"
	_attr_native_unit_of_measurement = CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
	_attr_device_class = SensorDeviceClass.PM25
	_attr_state_class = SensorStateClass.MEASUREMENT

	def update(self) -> None:
		"""Fetch new state data for the sensor.

		This is the only method that should fetch new data for Home Assistant.
		"""
		self._attr_native_value = self.readSensor()
		
	def readSensor(self) -> int:
		response  = requests.get("http://pa.willdarnell.net/json") # TODO: Pull from config
		json      = response.json()
		prefix    = "pm2_5_atm"
		readings  = [json[prefix], json[prefix + "_b"]]
		sensorAvg = round(sum(readings) / len(readings),1)
		return sensorAvg
	