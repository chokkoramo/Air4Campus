from datetime import datetime, timezone
from typing import Any

from entities.models import ClassroomConditions, ClassroomType, SensorValue
from interface_adapters.sensors.sensor_factory import SensorFactory


class IoTSensorAdapter:
    TIMESTAMP_FIELDS = ("ts", "timestamp", "timestamp_ms", "timestampMs", "timesnap", "time", "hora", "fecha")

    def __init__(self, sensor_factory: SensorFactory | None = None):
        self.sensor_factory = sensor_factory or SensorFactory()

    def to_classroom_conditions(self, payload: dict[str, Any]) -> ClassroomConditions:
        values = self._adapt_sensor_values(payload)

        return ClassroomConditions(
            ts=self._now(),
            device_id=payload.get("device_id"),
            classroom_id=payload.get("classroom_id"),
            classroom_type=self._parse_classroom_type(payload.get("classroom_type")),
            temperature=values.get("temperature", SensorValue.from_payload(payload.get("temperature"))),
            humidity=values.get("humidity", SensorValue.from_payload(payload.get("humidity"))),
            air_quality=values.get("air_quality", SensorValue.from_payload(payload.get("air_quality"))),
        )

    def _timestamp_value(self, payload: dict[str, Any]) -> Any:
        for field in self.TIMESTAMP_FIELDS:
            value = payload.get(field)
            if value is not None:
                return value

        return None

    def _parse_timestamp(self, value: Any) -> datetime:
        if isinstance(value, str):
            numeric_value = self._parse_numeric_timestamp(value)
            if numeric_value is not None:
                return self._parse_timestamp(numeric_value)

            try:
                return self._as_utc(datetime.fromisoformat(value.replace("Z", "+00:00")))
            except ValueError:
                return self._now()

        if value is None:
            return self._now()

        if isinstance(value, (int, float)):
            timestamp_seconds = value / 1000 if abs(value) >= 1_000_000_000_000 else value
            return datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)

        if isinstance(value, datetime):
            return self._as_utc(value)

        return self._now()

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _parse_numeric_timestamp(self, value: str) -> float | None:
        try:
            return float(value)
        except ValueError:
            return None

    def _as_utc(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

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
