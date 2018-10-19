import sys
sys.path.append('../app')


import json
import os
import shutil

import numpy as np

from config import get_config
from luftdaten.data import (
    get_luftdaten_raw_data_dir,
    get_luftdaten_aggregated_data_dir,
    get_existing_raw_luftdaten_filepaths,
    load_luftdaten_sensor_data,
    write_aggregated_dayofweek_data_files,
    write_24_hour_mean_aggregated_data_files,
)
from luftdaten.sensor import get_luftdaten_sensors


value_fields = ['P1', 'P2']
datetime_field = 'timestamp'


if __name__ == '__main__':
    data_dir = os.path.join('..', 'data')

    config_file_path = '../config/sensors.yaml'
    config = get_config(config_file_path)

    luftdaten_raw_data_dir = get_luftdaten_raw_data_dir(data_dir)
    luftdaten_aggregated_data_dir = get_luftdaten_aggregated_data_dir(data_dir)
    luftdaten_sensors = get_luftdaten_sensors(config)

    # Clear any previous runs of data
    if os.path.exists(luftdaten_aggregated_data_dir):
        shutil.rmtree(luftdaten_aggregated_data_dir)

    # Keep track of the years/months data available for each sensor
    sensors_info = []

    for sensor in luftdaten_sensors:
        sensor_code = sensor.code

        data = load_luftdaten_sensor_data(
            luftdaten_raw_data_dir,
            sensor_code,
            datetime_field
        )

        # Produce aggregated data files
        years_months_day_of_week = write_aggregated_dayofweek_data_files(
            luftdaten_aggregated_data_dir,
            sensor_code,
            data,
            value_fields,
            datetime_field
        )

        years_months_24_hour = write_24_hour_mean_aggregated_data_files(
            luftdaten_aggregated_data_dir,
            sensor_code,
            data,
            value_fields,
            datetime_field
        )

        # Remap year keys from integer to string (for JSON)
        years_months_24_hour = {
            str(key): val for key, val in years_months_24_hour.items()
        }
        years_months_day_of_week = {
            str(key): val for key, val in years_months_day_of_week.items()
        }

        sensor_config = config['sensors']['luftdaten'][sensor_code]
        sensors_info.append({
            'code': sensor_code,
            'name': sensor_config['name'],
            '24_hour_means': {
                'available_dates': years_months_24_hour
            },
            'day_of_week': {
                'available_dates': years_months_day_of_week
            }
        })

    # Write a summary file
    summary_json = {
        'luftdaten_sensors': sensors_info
    }
    summary_filepath = os.path.join(
        luftdaten_aggregated_data_dir,
        'sensor-summary.json'
    )

    def default(o):
        if isinstance(o, np.int64):
            return int(o)
        raise TypeError

    with open(summary_filepath, 'w') as output_file:
        json.dump(summary_json, output_file, default=default)
