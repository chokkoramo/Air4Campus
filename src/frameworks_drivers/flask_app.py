from flask import Flask

from frameworks_drivers.mongodb import create_sensor_repository
from interface_adapters.controllers.flask_routes import create_routes
from interface_adapters.presenters.json_presenter import JsonPresenter
from interface_adapters.sensors.iot_sensor_adapter import IoTSensorAdapter
from use_cases.alerts import AlertManager, MobileAlertObserver
from use_cases.analyze_classroom_conditions import AnalyzeClassroomConditions
from use_cases.query_sensor_data import GetRecentSensorReadings, QueryTimeSeries, SearchSensors
from use_cases.receive_sensor_data import ReceiveSensorData


def create_app() -> Flask:
    app = Flask(__name__)

    repository = create_sensor_repository()
    sensor_adapter = IoTSensorAdapter()
    presenter = JsonPresenter()
    alert_manager = AlertManager()
    alert_manager.attach(MobileAlertObserver())
    analyzer = AnalyzeClassroomConditions(alert_manager=alert_manager)

    app.register_blueprint(
        create_routes(
            search_sensors=SearchSensors(repository),
            query_time_series=QueryTimeSeries(repository),
            get_recent_readings=GetRecentSensorReadings(repository),
            receive_sensor_data=ReceiveSensorData(repository, analyzer),
            sensor_adapter=sensor_adapter,
            presenter=presenter,
        )
    )

    return app
