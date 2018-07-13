import sys
sys.path.append('../app')
import os
from datetime import datetime
import shutil

from config import get_config
from luftdaten.data import (
    get_luftdaten_raw_data_dir,
    get_luftdaten_aggregated_data_dir,
    get_existing_raw_luftdaten_filepaths,
)
from data import (
    create_24_hour_means,
    create_hourly_means_by_weekday_and_hour,
)
from luftdaten.sensor import get_luftdaten_sensors
import pandas as pd

value_fields = ['P1', 'P2']
datetime_field = 'timestamp'
sensor_type = 'sds011'

def load_luftdaten_sensor_data(luftdaten_raw_data_dir, sensor_code):
    """Loads all the raw data for a single luftdaten sensor."""
    converters = {}
    converters[datetime_field] = lambda val: datetime.strptime(val, "%Y-%m-%dT%H:%M:%S")

    # Aggregate the raw data into a single data frame for current sensor
    filepaths = get_existing_raw_luftdaten_filepaths(
        luftdaten_raw_data_dir,
        sensor_code
    )

    data = pd.DataFrame()
    for filepath in filepaths:
        data = data.append(
            pd.read_csv(
                filepath,
                delimiter=';',
                converters=converters
            )
        )
    return data

def _add_month_year_columns(data, datetime_field):
    """Adds month and year columns to a DataFrame using a timestamp column."""
    data['year'] = data[datetime_field].dt.year
    data['month'] = data[datetime_field].dt.month
    return data

def write_24_hour_mean_aggregated_data_files(luftdaten_aggregated_data_dir, sensor_code, data):
    """Writes aggregated data files to disk based on the raw data for a sensor.

    Produces aggregate output for each month"""
    df_24_hour_means = create_24_hour_means(
        raw_data=data,
        value_column=value_fields,
        date_column=datetime_field
    )

    # df_24_hour_means['year'] = df_24_hour_means[datetime_field].dt.year
    # df_24_hour_means['month'] = df_24_hour_means[datetime_field].dt.month
    df_24_hour_means = _add_month_year_columns(df_24_hour_means, datetime_field)

    data_24_hour_by_yearmonth = df_24_hour_means.groupby(
        [
            df_24_hour_means['year'],
            df_24_hour_means['month']
        ]
    )
    for (yearmonth, data_by_date) in data_24_hour_by_yearmonth:
        year, month = yearmonth

        output_filename = '{year}_{month:02d}_{sensor_type}_sensor_' \
            '{sensor_code}_24_hour_means.csv'.format(
                year=year,
                month=month,
                sensor_type=sensor_type,
                sensor_code=sensor_code
            )
        output_filepath = os.path.join(
            luftdaten_aggregated_data_dir,
            '24_hour_means',
            output_filename
        )
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        data_by_date.to_csv(output_filepath, index=False)

def write_aggregated_data_files(luftdaten_aggregated_data_dir, sensor_code, data):
    """Writes aggregated data files to disk based on the raw data for a sensor.

    Produces aggregate output for each month"""
    data = _add_month_year_columns(data, datetime_field)

    data_by_yearmonth = data.groupby([data['year'], data['month']])
    for (yearmonth, data_by_date) in data_by_yearmonth:
        year, month = yearmonth

        # Means by day/hour
        mean_by_weekday_and_hour = create_hourly_means_by_weekday_and_hour(
            raw_data=data_by_date,
            value_column=value_fields,
            date_column=datetime_field
        )
        mean_by_weekday_and_hour = _add_month_year_columns(
            mean_by_weekday_and_hour,
            datetime_field
        )
        output_filename = '{year}_{month:02d}_{sensor_type}_sensor_' \
            '{sensor_code}_by_weekday_by_hour.csv'.format(
                year=year,
                month=month,
                sensor_type=sensor_type,
                sensor_code=sensor_code
            )
        output_filepath = os.path.join(
            luftdaten_aggregated_data_dir,
            'weekday_by_hour',
            output_filename
        )
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        mean_by_weekday_and_hour.to_csv(output_filepath, index=False)

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

    for sensor in luftdaten_sensors:
        sensor_code = sensor.code

        data = load_luftdaten_sensor_data(
            luftdaten_raw_data_dir,
            sensor_code
        )

        # Produce aggreated data files
        write_aggregated_data_files(
            luftdaten_aggregated_data_dir,
            sensor_code,
            data
        )

        write_24_hour_mean_aggregated_data_files(
            luftdaten_aggregated_data_dir,
            sensor_code,
            data
        )
