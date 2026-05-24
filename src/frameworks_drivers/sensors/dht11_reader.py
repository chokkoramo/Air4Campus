class DHT11Reader:
    def __init__(self, sensor):
        self.sensor = sensor

    def read(self):
        self.sensor.measure()
        return {
            "type": "dht11",
            "temperature": self.sensor.temperature(),
            "temperature_unit": "C",
            "humidity": self.sensor.humidity(),
            "humidity_unit": "%",
        }
