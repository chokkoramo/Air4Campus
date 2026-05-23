from datetime import datetime
from typing import Any

from entities.models import ClassroomConditions, SensorValue


class IoTSensorAdapter:
    def to_classroom_conditions(self, payload: dict[str, Any]) -> ClassroomConditions:
        return ClassroomConditions(
            ts=self._parse_timestamp(payload.get("ts")),
            device_id=payload.get("device_id"),
            temperature=SensorValue.from_payload(payload.get("temperature")),
            humidity=SensorValue.from_payload(payload.get("humidity")),
            air_quality=SensorValue.from_payload(payload.get("air_quality")),
        )

    def _parse_timestamp(self, value: Any) -> datetime:
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return datetime.utcnow()

        if value is None:
            return datetime.utcnow()

        return value
