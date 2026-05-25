import time

class ESP32PayloadBuilder:
    def __init__(self, device_id, classroom_id=None, classroom_type="theoretical"):
        self.device_id = device_id
        self.classroom_id = classroom_id
        self.classroom_type = classroom_type

    def build(self, sensor_readings):
        payload = {
            "device_id": self.device_id,
            "classroom_id": self.classroom_id,
            "classroom_type": self.classroom_type,
            "ts": time.time(),
            "sensors": sensor_readings,
        }
        
        return payload