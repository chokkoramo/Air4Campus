from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


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

    def to_document(self) -> dict[str, Any]:
        return {
            "ts": self.ts,
            "device_id": self.device_id,
            "temperature": self.temperature.to_document(),
            "humidity": self.humidity.to_document(),
            "air_quality": self.air_quality.to_document(),
        }


@dataclass(frozen=True)
class ComfortAnalysis:
    status: ComfortStatus
    recommendations: list[str]
