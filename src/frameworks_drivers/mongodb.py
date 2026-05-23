import os
from datetime import datetime
from typing import Any

from pymongo import MongoClient

from entities.models import ClassroomConditions


class MongoSensorReadingRepository:
    def __init__(self, collection):
        self.collection = collection

    def distinct_data(self) -> list[Any]:
        return self.collection.distinct("data")

    def find_time_series(self, sensor_name: str, from_ts: datetime, to_ts: datetime) -> list[dict[str, Any]]:
        query = {
            "sensor": sensor_name,
            "ts": {"$gte": from_ts, "$lte": to_ts},
        }
        return list(self.collection.find(query).sort("ts", 1))

    def find_recent_readings(self, query: dict[str, Any], limit: int) -> list[dict[str, Any]]:
        return list(self.collection.find(query).sort("ts", -1).limit(limit))

    def insert(self, conditions: ClassroomConditions) -> str:
        result = self.collection.insert_one(conditions.to_document())
        return str(result.inserted_id)


def create_sensor_repository() -> MongoSensorReadingRepository:
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017/")
    db_name = os.environ.get("MONGO_DB", "test")

    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    db = client[db_name]
    return MongoSensorReadingRepository(db["data"])
