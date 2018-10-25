import datetime
import unittest

import numpy as np
import pandas as pd

from data.dataframe import (
    add_month_year_columns,
    create_24_hour_means,
    create_hourly_means_by_weekday_and_hour,
)


class TestAddMonthYearColumns(unittest.TestCase):

    def test_add_month_year_columns(self):
        df = pd.DataFrame({
            'data': [1, 2, 3, 4],
            'date': [
                datetime.datetime(2017, 1, 1),
                datetime.datetime(2017, 6, 1),
                datetime.datetime(2018, 1, 1),
                datetime.datetime(2018, 6, 1)
            ]
        })

        new_df = add_month_year_columns(df, 'date')

        self.assertTrue(
            np.array_equal(
                new_df.columns,
                ['data', 'date', 'year', 'month']
            )
        )

        self.assertEqual(new_df['year'][0], 2017)
        self.assertEqual(new_df['month'][0], 1)
        self.assertEqual(new_df['year'][1], 2017)
        self.assertEqual(new_df['month'][1], 6)
        self.assertEqual(new_df['year'][2], 2018)
        self.assertEqual(new_df['month'][2], 1)
        self.assertEqual(new_df['year'][3], 2018)
        self.assertEqual(new_df['month'][3], 6)


class TestCreate24HourMeans(unittest.TestCase):

    def test_create_24_hour_means(self):
        value_column = 'data'
        date_column = 'date'

        # Make 48 hours of data
        data = [
            {
                'date': datetime.datetime(2018, 6, 1) +
                    datetime.timedelta(hours=i),
                'data': float(i)
            }
            for i in range(48)
        ]
        raw_data = pd.DataFrame(data)

        # Run
        results = create_24_hour_means(
            raw_data, value_column, date_column
        )

        # Check results
        for i in range(48):
            # Pick last 24 hours data (if available)
            start_index = max((i + 1) - 24, 0)

            mean_24_hr_sum = sum(
                d[value_column]
                for d in data[start_index:i+1]
            )
            mean_24_hour_count = len(data[start_index:i+1])

            # Prevent divide by zero
            if mean_24_hr_sum == 0:
                mean_24_hr = 0
            else:
                mean_24_hr = float(mean_24_hr_sum) / mean_24_hour_count

            self.assertEqual(
                mean_24_hr, results[value_column][i]
            )


class TestcreateHourlyMeansByWeekdayAndHour(unittest.TestCase):

    def test_create_hourly_means_by_weekday_and_hour(self):
        value_column = 'data'
        date_column = 'date'

        # Make 6 weeks of half hourly data
        # Each hour has the same data value
        # Date starts from a Monday (first day of week in Python calendar)
        data = []
        for weeks in range(6):
            for days in range(7):
                for hours in range(24):
                    for min in [0, 30]:
                        date_ = datetime.datetime(2018, 10, 1) + \
                            datetime.timedelta(
                                weeks=weeks,
                                days=days,
                                hours=hours,
                                minutes=min
                            )
                        data.append({
                            'date': date_,
                            'data': float(days * hours)
                        })
        raw_data = pd.DataFrame(data)

        # Sense check data
        assert len(data) == 6 * 7 * 24 * 2
        assert max(d[date_column] for d in data), datetime.datetime(2018, 11, 11)
        # Check first value of week is repeated (1st, 2nd and last weeks)
        assert data[0][value_column] == \
               data[7 * 24 * 2][value_column] == \
               data[5 * 7 * 24 * 2][value_column]
        # Check last value of week is repeated (1st, 2nd and last weeks)
        assert data[(7 * 24 * 2) - 1][value_column] == \
               data[(2 * 7 * 24 * 2) - 1][value_column] == \
               data[(6 * 7 * 24 * 2) - 1][value_column]

        # Run
        results = create_hourly_means_by_weekday_and_hour(
            raw_data, value_column, date_column
        )

        # Check results
        self.assertEqual(len(results), 7 * 24)
        days_of_week = [
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
            'Sunday'
        ]
        for day_index, day_of_week in enumerate(days_of_week):
            day_data = results[results['dayOfWeek'] == day_of_week]
            self.assertEqual(len(day_data), 24)
            for hour in range(24):
                hour_data = day_data[day_data['hourOfDay'] == hour]
                self.assertEqual(len(hour_data), 1)
                self.assertEqual(hour_data[value_column].iloc[0], day_index * hour)
