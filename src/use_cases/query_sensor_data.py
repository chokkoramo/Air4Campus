from datetime import datetime
from typing import Any

from use_cases.ports import SensorReadingRepository


class SearchSensors:
    def __init__(self, repository: SensorReadingRepository):
        self.repository = repository

    def execute(self) -> list[Any]:
        return self.repository.distinct_data()


class QueryTimeSeries:
    def __init__(self, repository: SensorReadingRepository):
        self.repository = repository

    def execute(self, targets: list[dict[str, Any]], from_ts: datetime, to_ts: datetime) -> list[dict[str, Any]]:
        response = []

        for target in targets:
            sensor_name = target.get("target")
            documents = self.repository.find_time_series(sensor_name, from_ts, to_ts)
            datapoints = []

            for document in documents:
                value = document.get("value")
                ts = document.get("ts")
                if hasattr(ts, "timestamp"):
                    datapoints.append([value, int(ts.timestamp() * 1000)])

            response.append({"target": sensor_name, "datapoints": datapoints})

        return response


class GetRecentSensorReadings:
    SENSOR_FILTERS = {
        "temperature": ({"temperature.value": {"$exists": True}}, ("temperature", "value")),
        "humidity": ({"humidity.value": {"$exists": True}}, ("humidity", "value")),
        "air_quality": ({"air_quality.value": {"$exists": True}}, ("air_quality", "value")),
    }

    def __init__(self, repository: SensorReadingRepository):
        self.repository = repository

    def execute(self, sensor: str | None, limit: int) -> list[dict[str, Any]]:
        query, value_path = self.SENSOR_FILTERS.get(sensor, ({}, None))
        readings = self.repository.find_recent_readings(query, limit)

        if not value_path:
            return readings

        section, key = value_path
        for reading in readings:
            reading["value"] = reading.get(section, {}).get(key)

        return readings
