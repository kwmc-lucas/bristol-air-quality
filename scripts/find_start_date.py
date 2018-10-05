import argparse
import sys
sys.path.append('../app')

from luftdaten.data import find_start_date_for_sensor

parser = argparse.ArgumentParser(description='Find the earliest date of sensor data in Luftdaten archive.')
parser.add_argument('sensor_number', metavar='SensorNumber', type=int, nargs=1,
                    help='The sensor number')


if __name__ == '__main__':
    args = parser.parse_args()
    start_date = find_start_date_for_sensor(args.sensor_number[0])
    print("Earliest date found with data: ", start_date)
