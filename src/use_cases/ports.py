from datetime import datetime
from typing import Any, Protocol

from entities.models import ClassroomConditions


class SensorReadingRepository(Protocol):
    def distinct_data(self) -> list[Any]:
        ...

    def find_time_series(self, sensor_name: str, from_ts: datetime, to_ts: datetime) -> list[dict[str, Any]]:
        ...

    def find_recent_readings(self, query: dict[str, Any], limit: int) -> list[dict[str, Any]]:
        ...

    def insert(self, conditions: ClassroomConditions) -> str:
        ...
