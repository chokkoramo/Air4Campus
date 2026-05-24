from typing import Protocol

from entities.models import ClassroomConditions, ComfortAnalysis, ComfortStatus


class AlertObserver(Protocol):
    def update(self, conditions: ClassroomConditions, analysis: ComfortAnalysis) -> None:
        ...


class AlertManager:
    def __init__(self):
        self._observers: list[AlertObserver] = []

    def attach(self, observer: AlertObserver) -> None:
        self._observers.append(observer)

    def notify(self, conditions: ClassroomConditions, analysis: ComfortAnalysis) -> None:
        if analysis.status != ComfortStatus.CRITICAL:
            return

        for observer in self._observers:
            observer.update(conditions, analysis)


class MobileAlertObserver:
    def __init__(self):
        self.sent_alerts: list[dict[str, object]] = []

    def update(self, conditions: ClassroomConditions, analysis: ComfortAnalysis) -> None:
        self.sent_alerts.append(
            {
                "device_id": conditions.device_id,
                "classroom_id": conditions.classroom_id,
                "status": analysis.status.value,
                "alerts": analysis.alerts,
            }
        )
