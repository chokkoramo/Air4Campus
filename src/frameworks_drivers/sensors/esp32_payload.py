import time

class ESP32PayloadBuilder:
    def __init__(self, device_id, classroom_id=None, classroom_type="theoretical"):
        self.device_id = device_id
        self.classroom_id = classroom_id
        self.classroom_type = classroom_type

    def build(self, sensor_readings):
        temp = None
        hum = None
        aq = None

        for reading in sensor_readings:
            if isinstance(reading, dict):
                if "temperature" in reading:
                    temp = reading["temperature"]
                elif "temp" in reading:  
                    temp = reading["temp"]
                    
                if "humidity" in reading:
                    hum = reading["humidity"]
                elif "hum" in reading:   
                    hum = reading["hum"]
                    
                if "air_quality" in reading:
                    aq = reading["air_quality"]

        payload = {
            "device_id": self.device_id,
            "classroom_id": self.classroom_id,
            "classroom_type": self.classroom_type,
            "ts": time.time(),
            "temperature": temp,
            "humidity": hum,
            "air_quality": aq,
        }
        
        return payload