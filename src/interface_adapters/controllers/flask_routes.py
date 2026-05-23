from datetime import datetime

from flask import Blueprint, jsonify, request
from pymongo.errors import PyMongoError

from interface_adapters.presenters.json_presenter import JsonPresenter
from interface_adapters.sensors.iot_sensor_adapter import IoTSensorAdapter
from use_cases.query_sensor_data import GetRecentSensorReadings, QueryTimeSeries, SearchSensors
from use_cases.receive_sensor_data import ReceiveSensorData


def create_routes(
    search_sensors: SearchSensors,
    query_time_series: QueryTimeSeries,
    get_recent_readings: GetRecentSensorReadings,
    receive_sensor_data: ReceiveSensorData,
    sensor_adapter: IoTSensorAdapter,
    presenter: JsonPresenter,
) -> Blueprint:
    routes = Blueprint("air4campus_routes", __name__)

    @routes.route("/")
    def home():
        return "OK", 200

    @routes.route("/search", methods=["POST"])
    def search():
        try:
            return jsonify(search_sensors.execute())
        except Exception:
            return jsonify([])

    @routes.route("/query", methods=["POST"])
    def query():
        try:
            req = request.get_json(force=True)
            range_ = req.get("range", {})

            from_ts = datetime.fromisoformat(range_["from"].replace("Z", "+00:00"))
            to_ts = datetime.fromisoformat(range_["to"].replace("Z", "+00:00"))

            response = query_time_series.execute(req.get("targets", []), from_ts, to_ts)
            return jsonify(response)

        except Exception as exc:
            print("Query Error:", exc)
            return jsonify([])

    @routes.route("/json_api_data", methods=["GET", "POST"])
    def json_api_data():
        try:
            if request.method == "GET":
                sensor = request.args.get("sensor")
                limit = int(request.args.get("limit", 50))
            else:
                req = request.get_json(silent=True) or {}
                sensor = req.get("sensor")
                limit = int(req.get("limit", 50))

            data = get_recent_readings.execute(sensor, limit)
            return jsonify({"ok": True, "count": len(data), "data": presenter.readings(data)})

        except Exception as exc:
            return jsonify({"ok": False, "error": str(exc)}), 500

    @routes.route("/receive_sensor_data", methods=["POST"])
    def receive_sensor_data_route():
        payload = request.get_json(silent=True)

        if not payload:
            return jsonify({"ok": False, "error": "Invalid JSON"}), 400

        try:
            conditions = sensor_adapter.to_classroom_conditions(payload)
            inserted_id = receive_sensor_data.execute(conditions)
            return jsonify({"ok": True, "id": inserted_id}), 201

        except PyMongoError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 503

    return routes
