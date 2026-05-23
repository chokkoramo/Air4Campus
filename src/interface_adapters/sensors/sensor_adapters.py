from typing import Any, Protocol

from entities.models import SensorValue


class SensorAdapter(Protocol):
    sensor_type: str

    def adapt(self, payload: dict[str, Any]) -> dict[str, SensorValue]:
        ...


class DHT11Adapter:
    sensor_type = "dht11"

    def adapt(self, payload: dict[str, Any]) -> dict[str, SensorValue]:
        return {
            "temperature": SensorValue(
                value=_read_first(payload, "temperature", "temp"),
                unit=payload.get("temperature_unit", "C"),
            ),
            "humidity": SensorValue(
                value=_read_first(payload, "humidity", "hum"),
                unit=payload.get("humidity_unit", "%"),
            ),
        }


class MQ135Adapter:
    sensor_type = "mq135"

    def adapt(self, payload: dict[str, Any]) -> dict[str, SensorValue]:
        return {
            "air_quality": SensorValue(
                value=_read_first(payload, "air_quality", "gas", "ppm"),
                unit=payload.get("air_quality_unit", "ppm"),
            )
        }


def _read_first(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, dict):
            return value.get("value")
        if value is not None:
            return value

    return None
