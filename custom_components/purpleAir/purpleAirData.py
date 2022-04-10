import time
import requests
from datetime import datetime
from threading import Lock
from homeassistant.components.sensor import SensorDeviceClass

class conditionInfo():
	"""Helper class containing info about the monitored condition"""
	def __init__(self, name, unit, func, deviceClass = None, decimalPlaces = 0):
		self._name          = name
		self._unit          = unit
		self._func          = func          # Function to call to set a value based on the json pulled form the sensor
		self._deviceClass   = deviceClass
		self._decimalPlaces = decimalPlaces # Number of decimal places for any rounding

	@property
	def name(self):
		return self._name
		
	@property
	def unit(self):
		return self._unit

	@property
	def decimalPlaces(self):
		return self._decimalPlaces
	
	@property
	def deviceClass(self):
		return self._deviceClass
	
	@property
	def func(self):
		return self._func

class purpleAirData():
	"""Class that pulls data from the PurpleAir sensor and updates values for monitored conditions"""
	def __init__(self, url, freq, conditions):
		self._url        = url  # URL of the PA sensor (http://foo.bar/json)
		self._freq       = freq # Frequency to update
		self._values     = {}   # Dict of values for the current reading
		self._lastUpdate = -1

		# Init the list of values for the conditions we monitor
		for condition in conditions:
			self._values[condition] = 0.0 # Assume 0. May want to investigate defaults based on type or condition.

	@property
	def readings(self):
		lock = Lock()
		with lock:
			now = datetime.timestamp(datetime.now())
			if (now > self._lastUpdate + self._freq):
				self._lastUpdate = now
				self.__refreshData()
		return self._values

	def __refreshData(self):
		"""Get data from the PA sensor and update monitored conditions"""
		response  = requests.get(self._url)	# Read the sensor
		json      = response.json()         # Parse the JSON
		
		# Go update the conditions we were asked to monitor
		for condition in self.conditions:
			self._values[condition] = self.conditions[condition].func(self, json, condition)
		
	def __sensorAvg(self, json, condition) -> float:
		"""Sets a value based on the average of the A and B sensor. Assumes 'foo' and 'foo_b' in json"""
		info      = self.conditions[condition]
		readings  = self.__pairedReadings(json, condition) # Get the A and B values
		return round(sum(readings) / len(readings), info.decimalPlaces) # Compute the average and round
	
	def __singleValue(self, json, condition):
		"""Sets a value based on a single key in the json object"""
		return json[condition]
	
	def __pairedReadings(self, json, condition):
		"""Returns a list with the A and B values for a condition (e.g., 'foo' and 'foo_b')"""
		prefix = condition
		return [json[prefix], json[prefix + '_b']]
	
	def __health(self, json, condition) -> float:
		"""Computes and sets a synthetic health percentage by comparing A and B particle counters"""
		# TODO: Find a better algorithm
		readings = self.__pairedReadings(json, 'pm2_5_atm')
		return readings[0] / readings[1]

	### Master list of conditions that this implementation can monitor with helper object for how to process the metric
	conditions = { 
		  'pm2_5_atm'         : conditionInfo(name='PM 2.5',              unit='µg/m³', func=__sensorAvg,   deviceClass=SensorDeviceClass.PM25,        decimalPlaces=1)
		, 'pm10_0_atm'        : conditionInfo(name='PM 10',               unit='µg/m³', func=__sensorAvg,   deviceClass=SensorDeviceClass.PM10,        decimalPlaces=1)
		, 'pm2.5_aqi'         : conditionInfo(name='Air Quality Index',   unit='',      func=__sensorAvg,   deviceClass=SensorDeviceClass.AQI,         decimalPlaces=0)
		, 'health'            : conditionInfo(name='Sensor Health',       unit='',      func=__health                                                                 )
		, 'ssid'              : conditionInfo(name='WiFi SSID',           unit='',      func=__singleValue                                                            )
		, 'SensorId'          : conditionInfo(name='Sensor ID',           unit='',      func=__singleValue                                                            )
		, 'lat'               : conditionInfo(name='Latitude',            unit='°',     func=__singleValue                                                            )
		, 'lon'               : conditionInfo(name='Longitude',           unit='°',     func=__singleValue                                                            )
		, 'place'             : conditionInfo(name='Place',               unit='',      func=__singleValue                                                            )
		, 'current_temp_f'    : conditionInfo(name='Temperature',         unit='°F',    func=__singleValue, deviceClass=SensorDeviceClass.TEMPERATURE, decimalPlaces=1)
		, 'current_humidity'  : conditionInfo(name='Humidity',            unit='%',     func=__singleValue, deviceClass=SensorDeviceClass.HUMIDITY,    decimalPlaces=0)
		, 'current_dewpoint_f': conditionInfo(name='Dewpoint',            unit='°F',    func=__singleValue, deviceClass=SensorDeviceClass.TEMPERATURE, decimalPlaces=0)
		, 'pressure'          : conditionInfo(name='Barometric Pressure', unit='mbar',  func=__singleValue, deviceClass=SensorDeviceClass.PRESSURE,    decimalPlaces=2)
		, 'DateTime'          : conditionInfo(name='Timestamp',           unit='',      func=__singleValue                                                            )
	}
