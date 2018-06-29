import glob
import logging
import datetime
import os
import requests
import yaml
logger = logging.getLogger(__name__)

data_dir = os.path.join('..', 'data')
luftdaten_data_dir = os.path.join(data_dir, 'luftdaten')
luftdaten_raw_data_dir = os.path.join(luftdaten_data_dir, 'raw')

luftdaten_raw_filename_pattern = '{year}-{month}-{day}_sds011_sensor_{sensor_code}.csv'

class LatLongLocation(object):
    """Representation of latitude/longitude point."""
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

class Sensor(object):
    """A sensor for detecting environment measurements."""
    def __init__(self, code, name, start_date, location):
        self.code = code
        self.name = name
        self.start_date = start_date
        self.location = location

def validate_config(config):
    if not isinstance(config, dict):
        raise TypeError("Expected config object to be a dict")

    if 'sensors' not in config.keys():
        raise TypeError("Expected config to contain sensors section")

    sensors = config['sensors']
    luftdaten_sensors = sensors.get('luftdaten', {})

    if len(luftdaten_sensors) == 0:
        raise ValueError("Expected some luftdaten sensors to be defined in config")

    for sensor_code, sensor in luftdaten_sensors.items():
        if not isinstance(sensor, dict):
            raise TypeError("Expected luftdaten sensor config "
                            "object to be a dict")

        if 'name' not in sensor:
            raise TypeError("Expected luftdaten sensor config "
                            "object to have name")
        if not isinstance(sensor['name'], str):
            raise TypeError("Expected luftdaten sensor config "
                            "name to be string")

        if 'start_date' not in sensor:
            raise TypeError("Expected luftdaten sensor config "
                            "object to have start_date")
        if not isinstance(sensor['start_date'], datetime.date):
            raise TypeError("Expected luftdaten sensor config "
                            "start_date to be a date")

        if 'location' not in sensor:
            raise TypeError("Expected luftdaten sensor config "
                            "object to have location")
        if not isinstance(sensor['location'], dict):
            raise TypeError("Expected luftdaten sensor config "
                            "location to be dict")
        location = sensor['location']
        if 'latitude' not in location or \
            not isinstance(location['latitude'], float):
            raise TypeError("Expected luftdaten sensor config "
                            "location to have latitude (number)")
        if 'longitude' not in location or \
            not isinstance(location['longitude'], float):
            raise TypeError("Expected luftdaten sensor config "
                            "location to have longitude (number)")

def get_config():
    """Loads the sensor config file."""
    file_path = '../config/sensors.yaml'
    with open(file_path, 'r') as stream:
        try:
            config = yaml.load(stream)
        except yaml.YAMLError as exc:
            logger.exception("There was a problem opening the config file.")
            raise

    validate_config(config)

    return config

def get_luftdaten_sensors(config):
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

def get_luftdaten_raw_filename(sensor_code, date_):
    """Gets the filename of the sensor data file as used in the Luftdaten
    archive."""
    return luftdaten_raw_filename_pattern.format(
        year=date_.year,
        month="{:02d}".format(date_.month),
        day="{:02d}".format(date_.day),
        sensor_code=sensor_code
    )

def get_existing_raw_luftdaten_filenames(sensor_code):
    """Gets a list of luftdaten filenames that have been downloaded
    previously."""
    filename_glob = luftdaten_raw_filename_pattern.format(
        year='*',
        month='*',
        day='*',
        sensor_code=sensor_code
    )
    filepath_glob = os.path.join(luftdaten_raw_data_dir, "*", filename_glob)
    filepaths = glob.glob(filepath_glob)
    filenames = [os.path.basename(filepath) for filepath in filepaths]
    return filenames

def download_raw_luftdaten_files(sensor):
    """Downloads a mirror of Luftdaten archive files. Skips
    files downloaded before."""
    sensor_code = sensor.code

    # Find which files have been downloaded already and make a list of
    # missing files
    start_date = sensor.start_date
    end_date = datetime.date.today()
    date_delta = end_date - start_date

    required_filenames_list = []
    for date_offset in range(date_delta.days):
        requried_date = start_date + datetime.timedelta(days=date_offset)
        required_filenames_list.append(
            get_luftdaten_raw_filename(
                sensor_code,
                requried_date
            )
        )
    required_filenames = set(required_filenames_list)

    existing_filenames = set(
        get_existing_raw_luftdaten_filenames(sensor_code)
    )

    filenames_to_download = required_filenames - existing_filenames

    for filename in filenames_to_download:
        date_str = filename.split('_')[0]
        url = "http://archive.luftdaten.info/{date}/{filename}".format(
            date=date_str,
            filename=filename
        )
        filepath = os.path.join(luftdaten_raw_data_dir, date_str, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        # logger.info("Downloading {}".format(url))
        print("Downloading {}".format(url))
        request = requests.get(url)
        with open(filepath, 'w') as file_:
            file_.write(request.text)

    print("Downloading done")

def generate_luftdaten_data(config):
    luftdaten_sensors = get_luftdaten_sensors(config)
    for sensor in luftdaten_sensors:
        download_raw_luftdaten_files(sensor)
        # print(sensor.__dict__)

if __name__ == '__main__':
    config = get_config()
    generate_luftdaten_data(config)
