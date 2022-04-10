# purpleAir
Purple Air sensor integration for Home Assistant. A work in progress.

## What it does
This integration creates one sensor entity per monitored condition. As necessary, the integration will make an HTTP GET request to a PurpleAir sensor on your local LAN. The result will be decoded and the sensor values updated.

## Install
1. Clone or copy files to your Home Assistant environment
2. Edit your `configuration.yaml`
3. Restart Home Assistant

## Configuration
Sample configuration
``` yaml
sensor:
- platform: purpleAir
    url: "http://<MyPurpleAirSensor>/json"
    update_frequency: 60
    monitored_values:
      - pm2_5_atm
      - pm10_0_atm
```
The above configuration will make requests to a PurpleAir sensor at `<MyPurpleAirSensor>`. It will poll the sensor at most once every 60 seconds. It will create two sensor entities in Home Assistant, one for PM2.5 and one for PM10. For a list of supported conditions, see [purpleAirData.py](https://github.com/wrdarnell/purpleAir/blob/master/custom_components/purpleAir/purpleAirData.py).

## Limitations / To Do
* I am new to Home Assistant and Python. There may be better / more idiomatic ways to do accomplish my goals
* Can only interact with a single Purple Air sensor. A future update may allow for multiple sensors
* Could use the async treatment
* The health metric needs work. Still trying to find a calculation that will track the health percentage displayed on the PA website. Would be nice to trigger an alert if the sensor channels disagree too much
* Not all values returned in the JSON object from the sensor are available.
* This integration communicates with a Purple Air sensor directly over HTTP. A future version may allow for use of the PA API to read values from an arbitrary sensor
