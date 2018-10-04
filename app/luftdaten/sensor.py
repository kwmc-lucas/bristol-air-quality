from sensor import Sensor
from location import LatLongLocation


def get_luftdaten_sensors(config):
    """Get Luftdaten sensor inform from config"""
    luftdaten_sensors = config['sensors']['luftdaten']

    sensors = []
    for sensor_code, sensor_config in luftdaten_sensors.items():
        code = sensor_code
        name = sensor_config['name']
        start_date = sensor_config['start_date']
        latitude = sensor_config['location']['latitude']
        longitude = sensor_config['location']['longitude']
        location = LatLongLocation(latitude, longitude)
        sensor = Sensor(code, name, start_date, location)
        sensors.append(sensor)

    return sensors
