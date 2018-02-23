import argparse
from datetime import datetime
# import calendar
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from process import create_24_hour_means, create_hourly_means_by_weekday_and_hour

parser = argparse.ArgumentParser(description='Visualise Luftdaten data from download.')
parser.add_argument("sensorid", type=int, help="The sensor id")

args = parser.parse_args()

sensor_id = args.sensorid
value_field = 'P1'
datetime_field = 'timestamp'

# Read the data file for sensor
data_filename = 'luftdaten_sds011_sensor_{sensor_id}.csv'.format(sensor_id=sensor_id)
converters = {}
converters[datetime_field] = lambda val: datetime.strptime(val, "%Y-%m-%dT%H:%M:%S")
data = pd.read_csv(data_filename, converters=converters)

# 24 hour means
df_24_hour_means = create_24_hour_means(raw_data=data, value_column=value_field, date_column=datetime_field)
output_filename = 'luftdaten_sds011_sensor_{sensor_id}_24_hour_means.csv'.format(sensor_id=sensor_id)
df_24_hour_means.to_frame().to_csv(output_filename)

# Visualise 24 hour means
def visualise_24_hour_means(df_24_hour_means):
    # Plot the means by day/hour
    # fig, axes = plt.subplots(7, 1, figsize=(3, 12), subplot_kw={'ylim': (0, 60)})
    fig, axes = plt.subplots()

    df_24_hour_means.plot(ax=axes)

    # Add threshold
    # TODO: Change threshold for different particles
    threshold = df_24_hour_means.copy(deep=True)
    threshold[:] = 50
    threshold.plot(ax=axes)

    # plt.subplots_adjust(wspace=0, hspace=2)

    chart_filename = 'luftdaten_sds011_sensor_{sensor_id}_24_hour_means.png'.format(sensor_id=sensor_id)
    plt.savefig(chart_filename)

visualise_24_hour_means(df_24_hour_means)

# Means by day/hour
mean_by_weekday_and_hour = create_hourly_means_by_weekday_and_hour(raw_data=data, value_column=value_field, date_column=datetime_field)
output_filename = 'luftdaten_sds011_sensor_{sensor_id}_by_weekday_and_hour.csv'.format(sensor_id=sensor_id)
mean_by_weekday_and_hour.to_frame().to_csv(output_filename)

def visualise_day_hour_data(mean_by_weekday_and_hour):
    # Plot the means by day/hour
    fig, axes = plt.subplots(7, 1, figsize=(3, 12), subplot_kw={'ylim': (0, 60)})

    for i, weekday in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
        print(i)
        print(weekday)
        bar_data = mean_by_weekday_and_hour[weekday]
        # print(bar_data)
        bar_data.plot.bar(ax=axes[i], color='k', alpha=0.7, title=weekday)

    plt.subplots_adjust(wspace=0, hspace=2)

    chart_filename = 'luftdaten_sds011_sensor_{sensor_id}_by_weekday_and_hour.png'.format(sensor_id=sensor_id)
    plt.savefig(chart_filename)

visualise_day_hour_data(mean_by_weekday_and_hour)
