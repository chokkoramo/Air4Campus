from entities.models import ClassroomConditions
from use_cases.ports import SensorReadingRepository


class ReceiveSensorData:
    def __init__(self, repository: SensorReadingRepository):
        self.repository = repository

    def execute(self, conditions: ClassroomConditions) -> str:
        return self.repository.insert(conditions)
