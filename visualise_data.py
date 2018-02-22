import argparse
from datetime import datetime
import calendar
import requests
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Visualise Luftdaten data from download.')
parser.add_argument("sensorid", type=int, help="The sensor id")

args = parser.parse_args()

sensor_id = args.sensorid

data_filename = 'luftdaten_sds011_sensor_{sensor_id}.csv'.format(sensor_id=sensor_id)

converters = {
    'timestamp': lambda val: datetime.strptime(val, "%Y-%m-%dT%H:%M:%S")
}
data = pd.read_csv(data_filename, converters=converters)
data['dayOfWeek'] = data['timestamp'].map(lambda x: calendar.day_name[x.weekday()])
data['hourOfDay'] = data['timestamp'].map(lambda x: x.hour)

# print(data.head())
value_field = 'P1'
grouped = data[value_field].groupby([data['dayOfWeek'], data['hourOfDay']])

# print(grouped.head())

# print(grouped.mean())

output_filename = 'luftdaten_sds011_sensor_{sensor_id}_by_weekday_and_hour.csv'.format(sensor_id=sensor_id)

mean_by_weekday_and_hour = grouped.mean()

# print(mean_by_weekday_and_hour)

# Save aggregated data
mean_by_weekday_and_hour.to_frame().to_csv(output_filename)

# import matplotlib.pyplot as plt

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

# data.plot.barh(ax=axes[1], color='k', alpha=0.7)

# data['dt'] = data.apply(lambda row: datetime.strptime(row.timestamp, "%Y-%m-%dT%H:%M:%S"), axis=1)

# plt.rcParams['figure.figsize'] = (10.0, 8.0)
# plt.plot(data.dt, data.P2, linestyle = 'None', marker='.', markersize=1)
# plt.savefig("c:/temp/" + str(sensor_id) + ".png")
# data.to_csv("c:/temp/" + str(sensor_id) + ".csv")
