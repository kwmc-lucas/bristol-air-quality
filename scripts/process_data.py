import sys
sys.path.append('../app')

import calendar
from collections import defaultdict
import json
import os
from datetime import datetime
import shutil

import numpy
import pandas as pd

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

def _create_month_summary(month, filepath):
    """Dict summary of the information about a month's data."""
    summary_filepath = filepath[3:] \
        if filepath.startswith('../') else filepath
    return {
        'month': month,
        'month_name': calendar.month_name[month],
        'path': summary_filepath
    }

def write_24_hour_mean_aggregated_data_files(
    luftdaten_aggregated_data_dir,
    sensor_code,
    data
):
    """Writes 24 hour mean aggregated data files to disk based on the raw
    data for a sensor.

    Produces aggregate output split out for each month"""
    df_24_hour_means = create_24_hour_means(
        raw_data=data,
        value_column=value_fields,
        date_column=datetime_field
    )

    df_24_hour_means = _add_month_year_columns(df_24_hour_means, datetime_field)
    data_24_hour_by_yearmonth = df_24_hour_means.groupby(
        [df_24_hour_means['year'], df_24_hour_means['month']]
    )

    years_to_months = defaultdict(list)
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

        month_info = _create_month_summary(month, output_filepath)
        years_to_months[year].append(month_info)

    return years_to_months

def write_aggregated_dayofweek_data_files(
    luftdaten_aggregated_data_dir,
    sensor_code,
    data
):
    """Writes day of week aggregated data files to disk based on the raw
    data for a sensor.

    Produces aggregate output split out for each month."""
    data = _add_month_year_columns(data, datetime_field)

    data_by_yearmonth = data.groupby([data['year'], data['month']])
    years_to_months = defaultdict(list)
    for (yearmonth, data_by_date) in data_by_yearmonth:
        year, month = yearmonth

        if not isinstance(month, int):
            print(
                "WARNING: Expected month to be int, instead got "
                "{val} ({type_})".format(val=month, type_=type(month))
            )
            if isinstance(month, numpy.int64):
                month = int(month)
            elif isinstance(month, numpy.float64):
                if month == numpy.floor(month):
                    # Can safely convert to int
                    month = int(month)

            if not isinstance(month, int):
                raise ValueError(
                    "Expected month to be int, instead got "
                    "{val} ({type_})".format(val=month, type_=type(month))
                )

        # Means by day/hour
        mean_by_weekday_and_hour = create_hourly_means_by_weekday_and_hour(
            raw_data=data_by_date,
            value_column=value_fields,
            date_column=datetime_field
        )
        mean_by_weekday_and_hour['year'] = year
        mean_by_weekday_and_hour['month'] = month
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

        month_info = _create_month_summary(month, output_filepath)
        years_to_months[year].append(month_info)

    return years_to_months

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
            sensor_code
        )

        # Produce aggregated data files
        years_months_day_of_week = write_aggregated_dayofweek_data_files(
            luftdaten_aggregated_data_dir,
            sensor_code,
            data
        )

        years_months_24_hour = write_24_hour_mean_aggregated_data_files(
            luftdaten_aggregated_data_dir,
            sensor_code,
            data
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
        if isinstance(o, numpy.int64):
            return int(o)
        raise TypeError

    with open(summary_filepath, 'w') as output_file:
        json.dump(summary_json, output_file, default=default)
