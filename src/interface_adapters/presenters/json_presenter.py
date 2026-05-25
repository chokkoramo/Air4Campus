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
            
            data.append(item)

        return data

    def comfort_analysis(self, analysis: ComfortAnalysis) -> dict[str, Any]:
        return {
            "status": analysis.status.value,
            "recommendations": analysis.recommendations,
            "alerts": analysis.alerts,
        }