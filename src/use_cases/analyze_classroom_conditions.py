from entities.comfort_rules import analyze_comfort
from entities.models import ClassroomConditions, ComfortAnalysis


class AnalyzeClassroomConditions:
    def execute(self, conditions: ClassroomConditions) -> ComfortAnalysis:
        return analyze_comfort(conditions)
