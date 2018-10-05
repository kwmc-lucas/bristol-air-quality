import datetime
import unittest
from unittest.mock import patch

from luftdaten.data import (
    find_start_date_for_sensor,
    get_luftdaten_data_url,
    get_luftdaten_raw_filename,
)


class TestgetLuftdatenFilename(unittest.TestCase):

    def test_get_luftdaten_raw_filename(self):
        filename = get_luftdaten_raw_filename(12345, datetime.date(2018, 1, 31))
        self.assertEqual(filename, '2018-01-31_sds011_sensor_12345.csv')


class TestgetLuftdatenUrl(unittest.TestCase):

    def test_get_luftdaten_raw_filename(self):
        url = get_luftdaten_data_url(123, datetime.date(2017, 6, 1))
        self.assertEqual(
            url,
            'http://archive.luftdaten.info/2017-06-01/'
            '2017-06-01_sds011_sensor_123.csv'
        )


class MockRequestsResponse:
    """Dummy response for Requests library"""
    def __init__(self, status_code, text=None):
        self.status_code = status_code
        self.text = text or ''


# Source: https://stackoverflow.com/questions/15753390/how-can-i-mock-requests-and-the-response
# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    """Creates a dummy Requests response for requests.get"""
    url = args[0]

    # Mimic data available between 1 Jan 2018 and 1 Mar 2018
    date_str = url.split('/')[3]
    date_ = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    if date_ >= datetime.datetime(2018, 1, 1) and \
        date_ <= datetime.datetime(2018, 3, 1):
        return MockRequestsResponse(200)
    else:
        return MockRequestsResponse(404)


class TestFindStartDate(unittest.TestCase):

    def test_find_luftdaten_data_start_date(self):
        sensor_number = 123

        with patch('requests.get', side_effect=mocked_requests_get) as p:
            start_date = find_start_date_for_sensor(sensor_number)
            self.assertEqual(start_date, datetime.date(2018, 1, 1))

    def test_it_shouldnt_find_luftdaten_data_past_data_period_end(self):
        sensor_number = 123

        with patch('requests.get', side_effect=mocked_requests_get) as p:
            start_date = find_start_date_for_sensor(
                sensor_number,
                earliest_date=datetime.date(2018, 5, 1)
            )
            self.assertEqual(start_date, None)

    def test_it_shouldnt_find_luftdaten_data_before_data_period_begins(self):
        sensor_number = 123

        with patch('requests.get', side_effect=mocked_requests_get) as p:
            start_date = find_start_date_for_sensor(
                sensor_number,
                latest_date=datetime.date(2017, 9, 1)
            )
            self.assertEqual(start_date, None)
