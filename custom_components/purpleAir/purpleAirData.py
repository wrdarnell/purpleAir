import sched, time
import requests

class conditionInfo():
	"""Helper class containing info about the monitored condition"""
	def __init__(self, func, decimalPlaces = 0):
		self._func          = func          # Function to call to set a value based on the json pulled form the sensor
		self._decimalPlaces = decimalPlaces # Number of decimal places for any rounding

	@property
	def decimalPlaces(self):
		return self._decimalPlaces
	
	@property
	def func(self):
		return self._func

class purpleAirData():
	"""Class that pulls data from the PurpleAir sensor and updates values for monitored conditions"""
	def __init__(self, url, freq, conditions):
		self._url     = url  # URL of the PA sensor (http://foo.bar/json)
		self._freq    = freq # Frequency to update
		self._values  = {}   # Dict of values for the current reading

		# Init the list of values for the conditions we monitor
		for condition in conditions:
			self._values[condition] = 0.0 # Assume 0. May want to investigate defaults based on type or condition.

	def refreshData(self):
		"""Get data from the PA sensor and update monitored conditions"""
		response  = requests.get(self._url)	# Read the sensor
		json      = response.json()         # Parse the JSON
		
		# Go update the conditions we were asked to monitor
		for condition in self.conditions:
			self.conditions[condition].func(self, json, condition)
		
	def sensorAvg(self, json, condition):
		"""Sets a value based on the average of the A and B sensor. Assumes 'foo' and 'foo_b' in json"""
		info      = self.conditions[condition]
		readings  = self.pairedReadings(json, condition) # Get the A and B values
		sensorAvg = round(sum(readings) / len(readings), info.decimalPlaces) # Compute the average and round
		self.setValue(condition, sensorAvg) # Post it
	
	def singleValue(self, json, condition):
		"""Sets a value based on a single key in the json object"""
		self.setValue(condition, json[condition])
	
	def pairedReadings(self, json, condition):
		"""Returns a list with the A and B values for a condition (e.g., 'foo' and 'foo_b')"""
		prefix = condition
		return [json[prefix], json[prefix + '_b']]
	
	def setValue(self, condition, value):
		self._values[condition] = value

	def health(self, json, condition):
		"""Computes and sets a synthetic health percentage by comparing A and B particle counters"""
		# TODO: Find a better algorithm
		readings = self.pairedReadings(json, 'pm2_5_atm')
		self.setValue(condition, readings[1] / readings[0])

	### Master list of conditions that this implementation can monitor with helper object for how to process the metric
	conditions = { 
			  'pm2_5_atm'         : conditionInfo(func=sensorAvg,   decimalPlaces=1)
			, 'pm10_0_atm'        : conditionInfo(func=sensorAvg,   decimalPlaces=1)
			, 'pm2.5_aqi'         : conditionInfo(func=sensorAvg,   decimalPlaces=0)
			, 'health'            : conditionInfo(func=health                      )
			, 'ssid'              : conditionInfo(func=singleValue                 )
			, 'SensorId'          : conditionInfo(func=singleValue                 )
			, 'lat'               : conditionInfo(func=singleValue                 )
			, 'lon'               : conditionInfo(func=singleValue                 )
			, 'place'             : conditionInfo(func=singleValue                 )
			, 'current_temp_f'    : conditionInfo(func=singleValue                 )
			, 'current_humidity'  : conditionInfo(func=singleValue                 )
			, 'current_dewpoint_f': conditionInfo(func=singleValue                 )
			, 'pressure'          : conditionInfo(func=singleValue, decimalPlaces=2)
			, 'DateTime'          : conditionInfo(func=singleValue                 )
		}
