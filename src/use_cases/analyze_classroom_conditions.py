from entities.comfort_rules import ComfortRuleFactory
from entities.models import ClassroomConditions, ComfortAnalysis
from use_cases.alerts import AlertManager


class AnalyzeClassroomConditions:
    def __init__(
        self,
        comfort_rule_factory: ComfortRuleFactory | None = None,
        alert_manager: AlertManager | None = None,
    ):
        self.comfort_rule_factory = comfort_rule_factory or ComfortRuleFactory()
        self.alert_manager = alert_manager or AlertManager()

    def execute(self, conditions: ClassroomConditions) -> ComfortAnalysis:
        strategy = self.comfort_rule_factory.create(conditions.classroom_type)
        analysis = strategy.evaluate(conditions)
        self.alert_manager.notify(conditions, analysis)
        return analysis
