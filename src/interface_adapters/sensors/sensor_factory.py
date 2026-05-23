from interface_adapters.sensors.sensor_adapters import DHT11Adapter, MQ135Adapter, SensorAdapter


class SensorFactory:
    def __init__(self):
        self._adapters: dict[str, SensorAdapter] = {
            DHT11Adapter.sensor_type: DHT11Adapter(),
            MQ135Adapter.sensor_type: MQ135Adapter(),
        }

    def create(self, sensor_type: str) -> SensorAdapter:
        normalized_type = sensor_type.lower().replace("-", "")
        if normalized_type not in self._adapters:
            raise ValueError(f"Unsupported sensor type: {sensor_type}")

        return self._adapters[normalized_type]
