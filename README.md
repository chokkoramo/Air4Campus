# Air4Campus - IoT Air Quality Monitoring System

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-lightgrey)
![Render](https://img.shields.io/badge/Deploy-Render-orange)
![Grafana](https://img.shields.io/badge/Grafana-Dashboards-ff8800?logo=grafana)

## Overview

Air4Campus is a lightweight IoT system for monitoring indoor classroom conditions. ESP32 sensor nodes collect temperature, humidity, and air-quality readings, send them to a Flask API, and the API stores normalized readings in MongoDB Atlas for dashboards, querying, and comfort analysis.

The backend writes to the MongoDB database configured in `MONGO_URL`. In the normal project setup this is MongoDB Atlas, so every reading received by the Flask API is sent to Atlas. Local MongoDB is only useful for development if `MONGO_URL` is changed intentionally.

## Main Features

- Receives classroom sensor readings from ESP32 devices over HTTP.
- Supports DHT11 temperature/humidity and MQ135 air-quality readings.
- Accepts both a modern `sensors` array payload and legacy nested sensor fields.
- Normalizes timestamps before storing data in MongoDB.
- Stores `ts` as a MongoDB date and `timestamp_ms` as Unix epoch milliseconds.
- Generates a server timestamp when the device does not send one.
- Computes classroom comfort status: `optimal`, `regular`, or `critical`.
- Produces recommendations and alerts for out-of-range conditions.
- Exposes endpoints for recent readings and Grafana-style time-series queries.
- Runs locally with Python or Docker Compose.

## Hardware

| Component | Purpose | Notes |
| --- | --- | --- |
| ESP32 | Wi-Fi microcontroller | Sends JSON payloads to the Flask API |
| DHT11 | Temperature and humidity | Simple indoor sensor |
| MQ135 | Air-quality trend | Analog gas sensor; useful for relative changes |

## Architecture

```text
ESP32 -> Flask API -> MongoDB Atlas -> Grafana/API clients
```

The source code follows a layered structure:

- `entities`: domain models and classroom comfort rules.
- `use_cases`: application workflows for receiving, querying, and analyzing readings.
- `interface_adapters`: Flask controllers, JSON presenters, and sensor payload adapters.
- `frameworks_drivers`: MongoDB, Flask app wiring, and ESP32 MicroPython code.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Health check. Returns `OK`. |
| `POST` | `/receive_sensor_data` | Stores a sensor reading and returns comfort analysis. |
| `GET`/`POST` | `/json_api_data` | Returns recent readings. Optional `sensor` and `limit` filters. |
| `POST` | `/search` | Returns available sensor labels for dashboard discovery. |
| `POST` | `/query` | Returns Grafana-style time-series datapoints for a requested time range. |

## Sensor Payload

Preferred payload:

```json
{
  "device_id": "esp32_lab01",
  "classroom_id": "B-204",
  "classroom_type": "laboratory",
  "timestamp_ms": 1763749730000,
  "sensors": [
    {
      "type": "dht11",
      "temperature": 26,
      "humidity": 49
    },
    {
      "type": "mq135",
      "air_quality": 420
    }
  ]
}
```

Legacy payloads are also accepted:

```json
{
  "device_id": "esp32_lab01",
  "temperature": { "value": 26, "unit": "C" },
  "humidity": { "value": 49, "unit": "%" },
  "air_quality": { "value": 420, "unit": "ppm" }
}
```

## Timestamp Handling

The API accepts several timestamp field names so ESP32 firmware and clients can evolve without breaking the backend:

- `ts`
- `timestamp`
- `timestamp_ms`
- `timestampMs`
- `timesnap`
- `time`
- `hora`
- `fecha`

Accepted formats:

- ISO 8601 strings, for example `2025-11-21T18:28:50Z`.
- Unix epoch seconds, for example `1763749730`.
- Unix epoch milliseconds, for example `1763749730000`.
- Numeric strings with epoch seconds or milliseconds.

MongoDB stores:

- `ts`: normalized UTC MongoDB date, used for sorting and time-range queries.
- `timestamp_ms`: numeric Unix epoch milliseconds, useful for frontend clients and debugging.

If no timestamp is sent, the Flask backend uses the server receive time in UTC.

## MongoDB Document Shape

```json
{
  "ts": "2025-11-21T18:28:50Z",
  "timestamp_ms": 1763749730000,
  "device_id": "esp32_lab01",
  "classroom_id": "B-204",
  "classroom_type": "laboratory",
  "temperature": { "value": 26, "unit": "C" },
  "humidity": { "value": 49, "unit": "%" },
  "air_quality": { "value": 420, "unit": "ppm" },
  "comfort_analysis": {
    "status": "regular",
    "recommendations": ["Increase air renewal."],
    "alerts": []
  }
}
```

## Environment Variables

Create a `.env` file in the project root or configure these variables in Render:

```env
MONGO_URL=mongodb+srv://USER:PASS@cluster.mongodb.net/air4campus
MONGO_DB=air4campus
FLASK_ENV=development
PORT=7001
```

Only for local development, you can point `MONGO_URL` to the Docker MongoDB service instead of Atlas:

```env
MONGO_URL=mongodb://admin:admin123@mongo:27017/air4campus?authSource=admin
MONGO_DB=air4campus
```

## Run Locally with Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt
export MONGO_URL="mongodb://localhost:27017/"
export MONGO_DB="air4campus"
cd src
python app.py
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r src\requirements.txt
$env:MONGO_URL = "mongodb://localhost:27017/"
$env:MONGO_DB = "air4campus"
Set-Location src
python app.py
```

The API runs at `http://localhost:7001`.

## Run with Docker Compose

```bash
docker-compose up --build -d
docker-compose logs -f web
```

Services:

- Flask API: `http://localhost:7001`
- MongoDB: `localhost:27017` only if you intentionally use local MongoDB instead of Atlas
- Mongo Express: `http://localhost:8081` only for inspecting the optional local MongoDB container
- Grafana: `http://localhost:3000`

## Send a Reading

```bash
curl -X POST http://localhost:7001/receive_sensor_data \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "esp32_lab01",
    "classroom_id": "B-204",
    "classroom_type": "laboratory",
    "timestamp_ms": 1763749730000,
    "sensors": [
      { "type": "dht11", "temperature": 26, "humidity": 49 },
      { "type": "mq135", "air_quality": 420 }
    ]
  }'
```

Example response:

```json
{
  "ok": true,
  "id": "656000000000000000000000",
  "ts": 1763749730000,
  "comfort": {
    "status": "regular",
    "recommendations": ["Increase air renewal."],
    "alerts": []
  }
}
```

## Query Recent Data

```bash
curl "http://localhost:7001/json_api_data?sensor=temperature&limit=20"
```

Valid `sensor` filters:

- `temperature`
- `humidity`
- `air_quality`

If `sensor` is omitted, the endpoint returns recent full documents.

## Grafana Integration

The project includes endpoints that can be consumed by Grafana JSON data source plugins:

- `/search` for metric discovery.
- `/query` for time-series values.
- `/json_api_data` for recent raw readings.

Typical dashboard panels:

- Temperature over time.
- Relative humidity over time.
- MQ135 air-quality trend.
- Comfort status by classroom.
- Critical alerts and recommendations.

## ESP32 Firmware

MicroPython files for the ESP32 live in `src/frameworks_drivers/sensors`.

Important files:

- `main.py`: Wi-Fi connection, sensor loop, and HTTP POST.
- `config.example.py`: firmware configuration template.
- `dht11_reader.py`: DHT11 reader.
- `mq135_reader.py`: MQ135 reader.
- `esp32_payload.py`: payload builder.

The backend can timestamp readings automatically, so the ESP32 does not require an RTC to send valid data.

## Deployment on Render

1. Create a Render Web Service.
2. Point it to this repository.
3. Use `src` as the application directory if needed.
4. Install dependencies from `src/requirements.txt`.
5. Set `MONGO_URL`, `MONGO_DB`, and `FLASK_ENV`.
6. Allow Render network access in MongoDB Atlas.

## Future Improvements

- Persist alert delivery through email, SMS, or push notifications.
- Add authentication for write endpoints.
- Add automated tests for payload adapters and comfort rules.
- Add MongoDB indexes for large deployments.
- Improve MQ135 calibration per classroom.
- Add classroom maps and device management.

## License

This project is licensed under the Apache License 2.0. See `LICENSE` for details.
