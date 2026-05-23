from datetime import datetime
from typing import Any

from entities.models import ClassroomConditions, ClassroomType, SensorValue
from interface_adapters.sensors.sensor_factory import SensorFactory


class IoTSensorAdapter:
    def __init__(self, sensor_factory: SensorFactory | None = None):
        self.sensor_factory = sensor_factory or SensorFactory()

    def to_classroom_conditions(self, payload: dict[str, Any]) -> ClassroomConditions:
        values = self._adapt_sensor_values(payload)

        return ClassroomConditions(
            ts=self._parse_timestamp(payload.get("ts")),
            device_id=payload.get("device_id"),
            classroom_id=payload.get("classroom_id"),
            classroom_type=self._parse_classroom_type(payload.get("classroom_type")),
            temperature=values.get("temperature", SensorValue.from_payload(payload.get("temperature"))),
            humidity=values.get("humidity", SensorValue.from_payload(payload.get("humidity"))),
            air_quality=values.get("air_quality", SensorValue.from_payload(payload.get("air_quality"))),
        )

    def _parse_timestamp(self, value: Any) -> datetime:
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return datetime.utcnow()

        if value is None:
            return datetime.utcnow()

        if isinstance(value, (int, float)):
            return datetime.utcfromtimestamp(value)

        return value

    def _parse_classroom_type(self, value: Any) -> ClassroomType:
        try:
            return ClassroomType(value or ClassroomType.THEORETICAL)
        except ValueError:
            return ClassroomType.THEORETICAL

    def _adapt_sensor_values(self, payload: dict[str, Any]) -> dict[str, SensorValue]:
        values: dict[str, SensorValue] = {}
        sensor_payloads = payload.get("sensors")

        if not isinstance(sensor_payloads, list):
            return values

        for sensor_payload in sensor_payloads:
            if not isinstance(sensor_payload, dict):
                continue

            sensor_type = sensor_payload.get("type")
            if not sensor_type:
                continue

            adapter = self.sensor_factory.create(sensor_type)
            values.update(adapter.adapt(sensor_payload))

        return values
