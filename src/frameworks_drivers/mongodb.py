import os
from datetime import datetime
from pathlib import Path
from typing import Any

from pymongo import MongoClient

from entities.models import ClassroomConditions, ComfortAnalysis

ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT_DIR / ".env"

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

if load_dotenv:
    load_dotenv(ENV_FILE)
else:
    for line in ENV_FILE.read_text().splitlines() if ENV_FILE.exists() else []:
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


class DatabaseConnection:
    _client: MongoClient | None = None

    @classmethod
    def get_client(cls) -> MongoClient:
        if cls._client is None:
            mongo_url = _env("MONGO_URL", "mongodb://localhost:27017/")
            cls._client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)

        return cls._client


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

    def insert(self, conditions: ClassroomConditions, analysis: ComfortAnalysis | None = None) -> str:
        document = conditions.to_document()
        if analysis:
            document["comfort_analysis"] = {
                "status": analysis.status.value,
                "recommendations": analysis.recommendations,
                "alerts": analysis.alerts,
            }

        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    def ping(self) -> dict[str, Any]:
        self.collection.database.client.admin.command("ping")
        return {
            "database": self.collection.database.name,
            "collection": self.collection.name,
        }


def create_sensor_repository() -> MongoSensorReadingRepository:
    db_name = _env("MONGO_DB", "test")

    client = DatabaseConnection.get_client()
    db = client[db_name]
    return MongoSensorReadingRepository(db["data"])


def _env(name: str, default: str) -> str:
    value = os.environ.get(name, default).strip()
    return value.strip("\"'")
