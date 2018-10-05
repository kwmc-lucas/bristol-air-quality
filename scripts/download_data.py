import os
import sys
sys.path.append('../app')

from config import get_config
from luftdaten.data import download_luftdaten_data, get_luftdaten_raw_data_dir
from luftdaten.sensor import get_luftdaten_sensors

if __name__ == '__main__':
    data_dir = os.path.join('..', 'data')

    config_file_path = '../config/sensors.yaml'
    config = get_config(config_file_path)
    
    luftdaten_sensors = get_luftdaten_sensors(config)
    luftdaten_raw_data_dir = get_luftdaten_raw_data_dir(data_dir)
    download_luftdaten_data(luftdaten_raw_data_dir, luftdaten_sensors)
