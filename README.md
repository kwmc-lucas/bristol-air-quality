# Luftdaten Dashboard
Visualisation dashbaord based on data from [Luftdaten sensors](http://luftdaten.info).

The project has two parts:
- Some Python scripts to download and process Luftdaten data
- A website to visualise the processed data

## Installation
This project requires Python 3. Some Python libraries need to be installed:
```
# Create a virtual environment
$ python3 -m venv env

# Install via pip
$ env/bin/pip install -r requirements.txt
```

## Configuring the sensors config file
Edit the sensors.yaml file in the config directory to choose which sensors will be displayed.
You will need to know your id numbers for your Luftdaten sensors.

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
Before the website is viewable, you need to download and process the data:
```bash
# Download the data
env/bin/python download_data.py

# Process the data
env/bin/python process_data.py
```

## Running the website
After completing the steps above you'll be able to run the dashboard website:
```bash
# Start a web server, e.g.
python3 -m http.server # Python 3
# OR
python -m SimpleHTTPServer # Python 2.7
# Website should now be viewable at http://localhost:8000/
```

## Updating the data
You will to run the scripts in the 'Preparing the data' section above to update the data.

The scripts will only download new data to minimalize the impact on Luftdaten's servers.
 