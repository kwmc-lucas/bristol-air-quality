import argparse
import datetime
import requests
import pandas as pd
from io import StringIO

parser = argparse.ArgumentParser(description='Download Luftdaten data.')
parser.add_argument("sensorid", type=int, help="The sensor id")
parser.add_argument("numberdays", type=int, help="The number of days to fetch data")

args = parser.parse_args()

ndays = args.numberdays
sensor_id = args.sensorid

print(ndays, type(ndays))
print(sensor_id, type(sensor_id))

data = pd.DataFrame()
ldate = datetime.date.today() - datetime.timedelta(1)
for x in range(ndays):
    dt = str(ldate - datetime.timedelta(x))
    url = "http://archive.luftdaten.info/{dt}/{dt}_sds011_sensor_{sensor_id}.csv".format(dt=dt, sensor_id=sensor_id)
    print(url)
    r = requests.get(url)
    data = data.append(pd.read_csv(StringIO(r.text), delimiter=';'))

sorted_data = data.sort_values('timestamp', ascending=False)

output_filename = 'luftdaten_sds011_sensor_{sensor_id}.csv'.format(sensor_id=sensor_id)
# output_filename = 'luftdaten_sds011_sensor_{sensor_id}_{year}_{month:02}_{day:02}.csv'.format(
#     sensor_id=sensor_id, year=ldate.year, month=ldate.month, day=ldate.day)
sorted_data.to_csv(output_filename)
