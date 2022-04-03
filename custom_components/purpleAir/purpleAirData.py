import sched, time
import requests

class conditionInfo():
	def __init__(self, func, decimalPlaces = 0):
		self._func          = func
		self._decimalPlaces = decimalPlaces

	@property
	def decimalPlaces(self):
		return self._decimalPlaces
	
	@property
	def func(self):
		return self._func

class purpleAirData():
	def __init__(self, url, freq, conditions):
		self._url     = url
		self._freq    = freq
		self._sched   = sched.scheduler(time.time, time.sleep)
		self._values  = {}
		for condition in conditions:
			self._values[condition] = 0.0

	def refreshData(self):
		response  = requests.get(self._url)
		json      = response.json()
		
		for condition in self.conditions:
			self.setData(json, condition)

	def setData(self, json, condition):
		info = self.conditions[condition]
		info.func(self, json, condition)

	def getData(self, condition):
		return self._conditions[condition]
		
	def sensorAvg(self, json, condition):
		info      = self.conditions[condition]
		readings  = self.pairedReadings(json, condition)
		sensorAvg = round(sum(readings) / len(readings), info.decimalPlaces)
		self.setValue(condition, sensorAvg)
	
	def singleValue(self, json, condition):
		self.setValue(condition, json[condition])
	
	def pairedReadings(self, json, condition):
		prefix = condition
		return [json[prefix], json[prefix + '_b']]
	
	def setValue(self, condition, value):
		self._values[condition] = value

	def health(self, json, condition):
		readings = self.pairedReadings(json, 'pm2_5_atm')
		self.setValue(condition, readings[1] / readings[0])

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