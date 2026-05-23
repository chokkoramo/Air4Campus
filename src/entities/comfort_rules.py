from entities.models import ClassroomConditions, ComfortAnalysis, ComfortStatus


def analyze_comfort(conditions: ClassroomConditions) -> ComfortAnalysis:
    recommendations: list[str] = []
    critical = False
    regular = False

    temperature = conditions.temperature.value
    humidity = conditions.humidity.value
    air_quality = conditions.air_quality.value

    if temperature is not None:
        if temperature < 18 or temperature > 30:
            critical = True
            recommendations.append("Revisar ventilacion o climatizacion del aula.")
        elif temperature < 20 or temperature > 27:
            regular = True
            recommendations.append("Monitorear la temperatura del aula.")

    if humidity is not None:
        if humidity < 30 or humidity > 75:
            critical = True
            recommendations.append("Verificar humedad y ventilacion.")
        elif humidity < 40 or humidity > 65:
            regular = True
            recommendations.append("Monitorear humedad relativa.")

    if air_quality is not None:
        if air_quality > 700:
            critical = True
            recommendations.append("Activar ventilacion por calidad de aire critica.")
        elif air_quality > 400:
            regular = True
            recommendations.append("Aumentar renovacion de aire.")

    if critical:
        status = ComfortStatus.CRITICAL
    elif regular:
        status = ComfortStatus.REGULAR
    else:
        status = ComfortStatus.OPTIMAL

    return ComfortAnalysis(status=status, recommendations=recommendations)
