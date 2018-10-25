"""Pandas DataFrame helpers"""
import calendar


def _ensure_data_is_valid(data, date_column):
    """Checks whether there are any rows without a valid datetime."""
    null_time_rows = data[data[date_column].isnull()]
    if len(null_time_rows.index) > 0:
        raise ValueError("There are some non null time rows in the raw data")


def create_24_hour_means(raw_data, value_column, date_column):
    """Takes raw sensor data and produces 24 hour mean for each data point.

    :param raw_data: The raw sensor data to aggregate
    :type raw_data: DataFrame
    :param value_column: Name of the column with values to aggregate
    :type value_column: str
    :param date_column: Name of the datetime column
    :type date_column: str
    :returns: DataFrame containing rolling 24 hour means
    :rtype: DataFrame"""
    _ensure_data_is_valid(raw_data, date_column)

    df1 = raw_data.set_index(date_column).sort_index()
    df_24_hour_means = df1[value_column].rolling('24H').mean()
    return df_24_hour_means.reset_index()


def create_hourly_means_by_weekday_and_hour(raw_data, value_column, date_column):
    """Takes raw sensor data and produces hourly mean for each each weekday
    and hour.

    :param raw_data: The raw sensor data to aggregate
    :type raw_data: DataFrame
    :param value_column: Name of the column with values to aggregate
    :type value_column: str
    :param date_column: Name of the datetime column
    :type date_column: str
    :returns: DataFrame containing data grouped by day of week and hour of day
    :rtype: DataFrame"""
    _ensure_data_is_valid(raw_data, date_column)
    data = raw_data.copy()

    # Add extra of columns for day of week and hour of day
    data['dayOfWeek'] = data[date_column].map(lambda x: calendar.day_name[x.weekday()])
    data['hourOfDay'] = data[date_column].map(lambda x: x.hour)

    # Group the data by day of week and hour of day
    grouped = data[value_column].groupby([data['dayOfWeek'], data['hourOfDay']])
    mean_by_weekday_and_hour = grouped.mean()

    return mean_by_weekday_and_hour.reset_index()


def add_month_year_columns(data, datetime_field):
    """Adds month and year columns to a DataFrame using a timestamp column.

    :param data: The DataFrame
    :type data: DataFrame
    :param datetime_field: The datetime fields name
    :type datetime_field: str
    :returns: Altered DataFrame"""
    data['year'] = data[datetime_field].dt.year
    data['month'] = data[datetime_field].dt.month
    return data
