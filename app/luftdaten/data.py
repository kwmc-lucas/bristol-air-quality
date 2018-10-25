import calendar
from collections import defaultdict
import datetime
import glob
import logging
import os

import numpy as np
import pandas as pd
import requests

from data.dataframe import (
    add_month_year_columns,
    create_24_hour_means,
    create_hourly_means_by_weekday_and_hour,
)


logger = logging.getLogger(__name__)

luftdaten_raw_filename_pattern = '{year}-{month}-{day}_sds011_sensor_{sensor_code}.csv'

SENSOR_TYPE = 'sds011'


def get_luftdaten_raw_data_dir(data_dir):
    luftdaten_data_dir = os.path.join(data_dir, 'luftdaten')
    return os.path.join(luftdaten_data_dir, 'raw')


def get_luftdaten_aggregated_data_dir(data_dir):
    luftdaten_data_dir = os.path.join(data_dir, 'luftdaten')
    return os.path.join(luftdaten_data_dir, 'aggregated')


def get_luftdaten_raw_filename(sensor_code, date_):
    """Get the filename of the sensor data file as used in the Luftdaten
    archive."""
    return luftdaten_raw_filename_pattern.format(
        year=date_.year,
        month="{:02d}".format(date_.month),
        day="{:02d}".format(date_.day),
        sensor_code=sensor_code
    )


def get_luftdaten_data_url(sensor_code, date_):
    """Get the url of the data in Luftdaten archive"""
    filename = get_luftdaten_raw_filename(sensor_code, date_)
    date_str = filename.split('_')[0]
    return "http://archive.luftdaten.info/{date}/{filename}".format(
        date=date_str,
        filename=filename
    )


def load_luftdaten_sensor_data(
        luftdaten_raw_data_dir,
        sensor_code,
        datetime_field
):
    """Loads all the raw data for a single luftdaten sensor."""
    converters = {}
    converters[datetime_field] = \
        lambda val: datetime.datetime.strptime(val, "%Y-%m-%dT%H:%M:%S")

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


def find_start_date_for_sensor(sensor_code, earliest_date=None, latest_date=None, date_has_data_cache=None):
    """Finds the date for which data was first available in Luftdaten archives.

    Recursive function.
    Note: does a sparse search so might not find first data where sensor is available intermittently.

    :param sensor_code: The sensor code, as used by Luftdaten archives
    :param earliest_date: The earliest date with data so far
    :param latest_date: The latest date with data so far
    :param date_has_data_cache: Dict of dates to boolean to determine whether date has data
        (saves redundant calls to api)"""
    first_pass = earliest_date is None and latest_date is None
    earliest_date = earliest_date or datetime.date(2015, 10, 1)
    latest_date = latest_date or datetime.date.today()
    date_has_data_cache = date_has_data_cache or {}
    print(f"Searching between {earliest_date} and {latest_date}")

    # Find a distribution of dates between earliest/latest to check
    # Sometimes a sensor will go offline for day or two so worth checking
    # a spread of dates
    days_diff = (latest_date - earliest_date).days
    # print("no", sensor_code, days_diff)

    dates_sample = set()
    if days_diff == 0:
        dates_sample.add(earliest_date)
    if days_diff == 1:
        dates_sample.add(earliest_date)
        dates_sample.add(latest_date)
    else:
        # Aim for at least one date a month
        days_between_samples = min(int(days_diff / 3), 28)
        step_size = min(days_diff, days_between_samples)

        for day_offset in range(0, days_diff, max(step_size, 1)):
            dates_sample.add(earliest_date + datetime.timedelta(days=day_offset))

        # If this is the first run, include recent dates as the sensor may have only
        # just come online
        if first_pass:
            for i in range(7):
                dates_sample.add(
                    datetime.date.today() - datetime.timedelta(days=i)
                )

        dates_sample.add(latest_date)

    dates_to_check = sorted(list(dates_sample))

    date_has_data = {}
    for date_ in dates_to_check:
        if date_ in date_has_data_cache:
            date_has_data[date_] = date_has_data_cache[date_]
        else:
            url = get_luftdaten_data_url(sensor_code, date_)
            response = requests.get(url)
            has_data = response.status_code < 400
            print("Url {} {}".format(url, 'has data' if has_data else 'no data'))
            date_has_data[date_] = has_data
            date_has_data_cache[date_] = date_has_data[date_]

    if date_has_data[earliest_date]:
        # Earliest date has data, so we have our answer
        return earliest_date
    elif True not in date_has_data.values():
        # None of dates had data so we don't know when earliest period was
        return None
    elif len(dates_to_check) == 2:
        # Down to two dates - check which one has the data
        if date_has_data[dates_to_check[0]]:
            # Earliest date has data
            return dates_to_check[0]
        elif date_has_data[dates_to_check[1]]:
            # Latest date has data
            return dates_to_check[1]
        raise RuntimeError("Processing shouldn't get here")
    else:
        # Narrow down search
        last_date_with_missing_data = earliest_date
        for date_ in dates_to_check:
            if date_has_data[date_]:
                # We have a latest date for data, and a previous date without
                # data, so narrow down the search between the two
                return find_start_date_for_sensor(
                    sensor_code,
                    earliest_date=last_date_with_missing_data,
                    latest_date=date_,
                    date_has_data_cache=date_has_data_cache
                )
            last_date_with_missing_data = date_

        raise RuntimeError("Shouldn't get here")


def get_existing_raw_luftdaten_filepaths(luftdaten_raw_data_dir, sensor_code):
    """Gets a list of luftdaten filepaths that have been downloaded
    previously."""
    filename_glob = luftdaten_raw_filename_pattern.format(
        year='*',
        month='*',
        day='*',
        sensor_code=sensor_code
    )
    filepath_glob = os.path.join(luftdaten_raw_data_dir, "*", filename_glob)
    return glob.glob(filepath_glob)


def get_existing_raw_luftdaten_filenames(luftdaten_raw_data_dir, sensor_code):
    """Gets a list of luftdaten filenames that have been downloaded
    previously."""
    filepaths = get_existing_raw_luftdaten_filepaths(
        luftdaten_raw_data_dir,
        sensor_code
    )
    filenames = [os.path.basename(filepath) for filepath in filepaths]
    return filenames


def download_raw_luftdaten_files(luftdaten_raw_data_dir, sensor):
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
        get_existing_raw_luftdaten_filenames(
            luftdaten_raw_data_dir,
            sensor_code
        )
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
        reponse = requests.get(url)
        if reponse.status_code == requests.codes.ok:
            with open(filepath, 'w') as file_:
                file_.write(reponse.text)
        else:
            print(
                "WARNING: {url} download failed with http status code"
                " {status_code}".format(
                    url=url,
                    status_code=reponse.status_code
                )
            )

    print("Downloading done")


def download_luftdaten_data(luftdaten_raw_data_dir, luftdaten_sensors):
    for sensor in luftdaten_sensors:
        download_raw_luftdaten_files(
            luftdaten_raw_data_dir,
            sensor
        )


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
    data,
    value_fields,
    datetime_field
):
    """Writes 24 hour mean aggregated data files to disk based on the raw
    data for a sensor.

    Produces aggregate output split out for each month"""
    df_24_hour_means = create_24_hour_means(
        raw_data=data,
        value_column=value_fields,
        date_column=datetime_field
    )

    df_24_hour_means = add_month_year_columns(df_24_hour_means, datetime_field)
    data_24_hour_by_yearmonth = df_24_hour_means.groupby(
        [
            df_24_hour_means['year'],
            df_24_hour_means['month']
        ]
    )

    years_to_months = defaultdict(list)
    for (yearmonth, data_by_date) in data_24_hour_by_yearmonth:
        year, month = yearmonth

        output_filename = '{year}_{month:02d}_{sensor_type}_sensor_' \
            '{sensor_code}_24_hour_means.csv'.format(
                year=year,
                month=month,
                sensor_type=SENSOR_TYPE,
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
    data,
    value_fields,
    datetime_field
):
    """Writes day of week aggregated data files to disk based on the raw
    data for a sensor.

    Produces aggregate output split out for each month."""
    data = add_month_year_columns(data, datetime_field)

    data_by_yearmonth = data.groupby([data['year'], data['month']])
    years_to_months = defaultdict(list)
    for (yearmonth, data_by_date) in data_by_yearmonth:
        year, month = yearmonth

        if not isinstance(month, int):
            print(
                "WARNING: Expected month to be int, instead got "
                "{val} ({type_})".format(val=month, type_=type(month))
            )
            if isinstance(month, np.int64):
                month = int(month)
            elif isinstance(month, np.float64):
                if month == np.floor(month):
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
                sensor_type=SENSOR_TYPE,
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
