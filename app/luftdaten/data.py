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
    """Gets the filename of the sensor data file as used in the Luftdaten
    archive."""
    return luftdaten_raw_filename_pattern.format(
        year=date_.year,
        month="{:02d}".format(date_.month),
        day="{:02d}".format(date_.day),
        sensor_code=sensor_code
    )


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
