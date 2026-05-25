from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ClassroomType(str, Enum):
    THEORETICAL = "theoretical"
    LABORATORY = "laboratory"


class ComfortStatus(str, Enum):
    OPTIMAL = "optimal"
    REGULAR = "regular"
    CRITICAL = "critical"


@dataclass(frozen=True)
class SensorValue:
    value: float | int | None
    unit: str | None = None

    @classmethod
    def from_payload(cls, payload: dict[str, Any] | None) -> "SensorValue":
        if not isinstance(payload, dict):
            return cls(value=None, unit=None)

        return cls(value=payload.get("value"), unit=payload.get("unit"))

    def to_document(self) -> dict[str, Any] | None:
        if self.value is None and self.unit is None:
            return None

        return {"value": self.value, "unit": self.unit}


@dataclass(frozen=True)
class ClassroomConditions:
    ts: datetime
    device_id: str | None
    temperature: SensorValue
    humidity: SensorValue
    air_quality: SensorValue
    classroom_id: str | None = None
    classroom_type: ClassroomType = ClassroomType.THEORETICAL

    def to_document(self) -> dict[str, Any]:
        ts = self._normalized_ts()

        return {
            "ts": ts,
            "timestamp_ms": int(ts.timestamp() * 1000),
            "device_id": self.device_id,
            "classroom_id": self.classroom_id,
            "classroom_type": self.classroom_type.value,
            "temperature": self.temperature.to_document(),
            "humidity": self.humidity.to_document(),
            "air_quality": self.air_quality.to_document(),
        }

    def _normalized_ts(self) -> datetime:
        if self.ts.tzinfo is None:
            return self.ts.replace(tzinfo=timezone.utc)

        return self.ts.astimezone(timezone.utc)


@dataclass(frozen=True)
class ComfortAnalysis:
    status: ComfortStatus
    recommendations: list[str]
    alerts: list[str]
