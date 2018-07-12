import sys
sys.path.append('../app')
import os
from datetime import datetime
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

def write_aggregated_data_files(luftdaten_aggregated_data_dir, sensor_code, data):
    """Writes aggregated data files to disk based on the raw data for a sensor.
    Produces aggregate output for each month"""
    # 24 hour means
    df_24_hour_means = create_24_hour_means(
        raw_data=data,
        value_column=value_fields,
        date_column=datetime_field
    ).reset_index()

    df_24_hour_means['year'] = df_24_hour_means[datetime_field].dt.year
    df_24_hour_means['month'] = df_24_hour_means[datetime_field].dt.month
    print(data.head())

    data_24_hour_by_yearmonth = df_24_hour_means.groupby(
        [
            df_24_hour_means['year'],
            df_24_hour_means['month']
        ]
    )
    for (yearmonth, data_by_date) in data_24_hour_by_yearmonth:
        year, month = yearmonth
        print(year, month)

        output_filename = '{year}_{month:02d}_sds011_sensor_' \
            '{sensor_code}_24_hour_means.csv'.format(
            year=year,
            month=month,
            sensor_code=sensor_code
        )
        output_filepath = os.path.join(
            luftdaten_aggregated_data_dir,
            '24_hour_means',
            output_filename
        )
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        data_by_date.to_csv(output_filepath)


    data['year'] = data[datetime_field].dt.year
    data['month'] = data[datetime_field].dt.month

    data_by_yearmonth = data.groupby([data['year'], data['month']])
    for (yearmonth, data_by_date) in data_by_yearmonth:
        year, month = yearmonth
        print(year, month)

        raise ValueError("Merge value fields into same file")
        for value_field in value_fields:

            # Means by day/hour
            mean_by_weekday_and_hour = create_hourly_means_by_weekday_and_hour(
                raw_data=data_by_date,
                value_column=value_field,
                date_column=datetime_field
            )
            output_filename = '{year}_{month:02d}_sds011_sensor_{sensor_code}_by_weekday_by_hour.csv'.format(
                year=year,
                month=month,
                sensor_code=sensor_code
            )
            output_filepath = os.path.join(
                luftdaten_aggregated_data_dir,
                'weekday_by_hour',
                output_filename
            )
            os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
            mean_by_weekday_and_hour.to_frame().to_csv(output_filepath)

if __name__ == '__main__':
    data_dir = os.path.join('..', 'data')

    config_file_path = '../config/sensors.yaml'
    config = get_config(config_file_path)

    luftdaten_raw_data_dir = get_luftdaten_raw_data_dir(data_dir)
    luftdaten_aggregated_data_dir = get_luftdaten_aggregated_data_dir(data_dir)
    luftdaten_sensors = get_luftdaten_sensors(config)

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
