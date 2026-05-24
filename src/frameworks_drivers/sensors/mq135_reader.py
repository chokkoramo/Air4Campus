class MQ135Reader:
    def __init__(self, adc, conversion_factor=1.0):
        self.adc = adc
        self.conversion_factor = conversion_factor

    def read(self):
        raw_value = self.adc.read()
        return {
            "type": "mq135",
            "air_quality": raw_value * self.conversion_factor,
            "air_quality_unit": "ppm",
            "raw": raw_value,
        }
