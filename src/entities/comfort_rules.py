from typing import Protocol

from entities.models import ClassroomConditions, ClassroomType, ComfortAnalysis, ComfortStatus


class ComfortRuleStrategy(Protocol):
    def evaluate(self, conditions: ClassroomConditions) -> ComfortAnalysis:
        ...


class TheoreticalClassroomComfortRule:
    def evaluate(self, conditions: ClassroomConditions) -> ComfortAnalysis:
        return _evaluate_with_thresholds(
            conditions=conditions,
            temperature_regular=(20, 27),
            temperature_critical=(18, 30),
            humidity_regular=(40, 65),
            humidity_critical=(30, 75),
            air_quality_regular=400,
            air_quality_critical=700,
        )


class LaboratoryComfortRule:
    def evaluate(self, conditions: ClassroomConditions) -> ComfortAnalysis:
        return _evaluate_with_thresholds(
            conditions=conditions,
            temperature_regular=(19, 26),
            temperature_critical=(17, 29),
            humidity_regular=(35, 60),
            humidity_critical=(25, 70),
            air_quality_regular=300,
            air_quality_critical=550,
        )


class ComfortRuleFactory:
    def create(self, classroom_type: ClassroomType) -> ComfortRuleStrategy:
        if classroom_type == ClassroomType.LABORATORY:
            return LaboratoryComfortRule()

        return TheoreticalClassroomComfortRule()


def analyze_comfort(conditions: ClassroomConditions) -> ComfortAnalysis:
    strategy = ComfortRuleFactory().create(conditions.classroom_type)
    return strategy.evaluate(conditions)


def _evaluate_with_thresholds(
    conditions: ClassroomConditions,
    temperature_regular: tuple[int, int],
    temperature_critical: tuple[int, int],
    humidity_regular: tuple[int, int],
    humidity_critical: tuple[int, int],
    air_quality_regular: int,
    air_quality_critical: int,
) -> ComfortAnalysis:
    recommendations: list[str] = []
    alerts: list[str] = []
    critical = False
    regular = False

    temperature = conditions.temperature.value
    humidity = conditions.humidity.value
    air_quality = conditions.air_quality.value

    if temperature is not None:
        if temperature < temperature_critical[0] or temperature > temperature_critical[1]:
            critical = True
            alerts.append("Temperatura en nivel critico.")
            recommendations.append("Revisar ventilacion o climatizacion del aula.")
        elif temperature < temperature_regular[0] or temperature > temperature_regular[1]:
            regular = True
            recommendations.append("Monitorear la temperatura del aula.")

    if humidity is not None:
        if humidity < humidity_critical[0] or humidity > humidity_critical[1]:
            critical = True
            alerts.append("Humedad en nivel critico.")
            recommendations.append("Verificar humedad y ventilacion.")
        elif humidity < humidity_regular[0] or humidity > humidity_regular[1]:
            regular = True
            recommendations.append("Monitorear humedad relativa.")

    if air_quality is not None:
        if air_quality > air_quality_critical:
            critical = True
            alerts.append("Calidad del aire en nivel critico.")
            recommendations.append("Activar ventilacion por calidad de aire critica.")
        elif air_quality > air_quality_regular:
            regular = True
            recommendations.append("Aumentar renovacion de aire.")

    if critical:
        status = ComfortStatus.CRITICAL
    elif regular:
        status = ComfortStatus.REGULAR
    else:
        status = ComfortStatus.OPTIMAL

    return ComfortAnalysis(status=status, recommendations=recommendations, alerts=alerts)
