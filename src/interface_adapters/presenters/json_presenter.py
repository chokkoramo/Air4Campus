from typing import Any
from entities.models import ComfortAnalysis


class JsonPresenter:
    def readings(self, documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        data = []

        for document in documents:
            item = dict(document)
            
            if "_id" in item:
                item["_id"] = str(item["_id"])

            ts = item.get("ts")
            if hasattr(ts, "timestamp"):
                item["ts"] = int(ts.timestamp() * 1000)

            if "sensors" in item and isinstance(item["sensors"], list):
                for sensor in item["sensors"]:
                    if "temperature" in sensor:
                        item["temperature"] = sensor.get("temperature")
                    if "humidity" in sensor:
                        item["humidity"] = sensor.get("humidity")
                    if "air_quality" in sensor:
                        item["air_quality"] = sensor.get("air_quality")
                
                item.pop("sensors", None)
            
            item.setdefault("temperature", None)
            item.setdefault("humidity", None)
            item.setdefault("air_quality", None)

            data.append(item)

        return data

    def comfort_analysis(self, analysis: ComfortAnalysis) -> dict[str, Any]:
        return {
            "status": analysis.status.value,
            "recommendations": analysis.recommendations,
            "alerts": analysis.alerts,
        }