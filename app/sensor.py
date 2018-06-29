class Sensor(object):
    """A sensor for detecting environment measurements."""
    def __init__(self, code, name, start_date, location):
        self.code = code
        self.name = name
        self.start_date = start_date
        self.location = location
