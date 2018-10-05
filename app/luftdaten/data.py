import datetime
import glob
import logging
import os

import requests


logger = logging.getLogger(__name__)

luftdaten_raw_filename_pattern = '{year}-{month}-{day}_sds011_sensor_{sensor_code}.csv'


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


def find_start_date_for_sensor(sensor_code, earliest_date=None, latest_date=None, date_has_data_cache=None):
    """Finds the date for which data was first available in Luftdaten archives.

    Recursive function.
    Note: does a sparse search so might not find first data where sensor is available intermittently.

    :param sensor_code: The sensor code, as used by Luftdaten archives
    :param earliest_date: The earliest date with data so far
    :param latest_date: The latest date with data so far
    :param date_has_data_cache: Dict of dates to boolean to determine whether date has data
        (saves redundant calls to api)"""
    earliest_date = earliest_date or datetime.date(2015, 10, 1)
    latest_date = latest_date or datetime.date.today()
    date_has_data_cache = date_has_data_cache or {}
    print(f"Searching between {earliest_date} and {latest_date}")

    # Find a distribution of dates between earliest/latest to check
    # Sometimes a sensor will go offline for day or two so worth checking
    # a spread of dates
    days_diff = (latest_date - earliest_date).days
    # print("no", sensor_code, days_diff)

    dates_to_check = []
    if days_diff == 0:
        dates_to_check.append(earliest_date)
    if days_diff == 1:
        dates_to_check.append(earliest_date)
        dates_to_check.append(latest_date)
    else:
        for day_offset in range(0, days_diff, min(days_diff, int(days_diff / 5))):
            dates_to_check.append(earliest_date + datetime.timedelta(days=day_offset))
    if dates_to_check[-1] != latest_date:
        dates_to_check.append(latest_date)

    assert len(dates_to_check) == len(set(dates_to_check))

    date_has_data = {}
    for date_ in dates_to_check:
        if date_ in date_has_data_cache:
            date_has_data[date_] = date_has_data_cache[date_]
        else:
            url = get_luftdaten_data_url(sensor_code, date_)
            print("Checking {}".format(url))
            response = requests.get(url)
            date_has_data[date_] = response.status_code < 400
            date_has_data_cache[date_] = date_has_data[date_]
    # print(dates_to_check)
    # print(date_has_data)

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
