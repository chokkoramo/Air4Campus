from dataclasses import dataclass

from entities.models import ClassroomConditions
from use_cases.analyze_classroom_conditions import AnalyzeClassroomConditions
from use_cases.ports import SensorReadingRepository


@dataclass(frozen=True)
class ReceiveSensorDataResult:
    inserted_id: str
    status: str
    recommendations: list[str]
    alerts: list[str]


class ReceiveSensorData:
    def __init__(
        self,
        repository: SensorReadingRepository,
        analyzer: AnalyzeClassroomConditions | None = None,
    ):
        self.repository = repository
        self.analyzer = analyzer or AnalyzeClassroomConditions()

    def execute(self, conditions: ClassroomConditions) -> ReceiveSensorDataResult:
        analysis = self.analyzer.execute(conditions)
        inserted_id = self.repository.insert(conditions, analysis)

        return ReceiveSensorDataResult(
            inserted_id=inserted_id,
            status=analysis.status.value,
            recommendations=analysis.recommendations,
            alerts=analysis.alerts,
        )
