# Luftdaten Dashboard
Visualisation dashbaord based on data from [Luftdaten sensors](http://luftdaten.info).

The project has two parts:
- Some Python scripts to download and process Luftdaten data
- A website to visualise the processed data

## Installation
This project requires Python 3. Some Python libraries need to be installed:
```
# Create a virtual environment
python3 -m venv env

# Install via pip
env/bin/pip install -r requirements.txt
```

## Configuring the sensors config file
Edit the sensors.yaml file in the config directory to choose which sensors will be displayed.
You will need to know your id numbers for your Luftdaten sensors. You will get your sensor
id when you register your sensor on the Luftdaten site (https://luftdaten.info/en/construction-manual/).  

You can use a script in this project to help find the first date a sensor came online. You'll
need this for the 'start_date' attribute in you config file. Note the script samples dates from
Luftdaten archives, so it might not find the true start date if the sensor data is intermittent.
To run the script:

```bash
cd scripts

# Substitute your sensor id for SENSOR_ID below
../env/bin/python find_start_date.py SENSOR_ID
```

Alternatively you can find the start date by browsing the 
[Luftdaten archives](http://archive.luftdaten.info) to see when the data files
first appear for the sensor.

Follow the format in the YAML file, copying and pasting to create more sensors:
```yaml
sensors:
    luftdaten:
        # Change the number 7675 to your sensor number and update
        # the text details beneath it
        7675:
            name: St Werburghs - The Yard north
            start_date: 2018-05-01
            location:
                latitude: 51.474708
                longitude: -2.576841
        # Add more sensors by copying and pasting the section above, e.g:
        # 7676:
        #   name: My other sensor
        #   ...
```

## Preparing the data
This project uses data from the [Luftdaten data archives](http://archive.luftdaten.info).
It fetches data based on the sensors listed in the config file (see above).

Before the dashboard website is viewable, you need to download and process the data:
```bash
cd scripts

# Download the data
../env/bin/python download_data.py

# Process the data
../env/bin/python process_data.py

# Return to the top level directory
cd ..
```

## Running the website
After completing the steps above you'll be able to run the dashboard website:
```bash
# Start a local web server from the top level directory, e.g:
python3 -m http.server
# Website should now be viewable at http://localhost:8000/
```

## Updating the data
You will need to run the scripts in the 'Preparing the data' section above to update the data.

The scripts will only download new data to minimalize the impact on Luftdaten's servers.
 