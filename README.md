# Air4Campus — IoT Air Quality Monitoring System

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
![Render](https://img.shields.io/badge/Deploy-Render-orange)
![Grafana](https://img.shields.io/badge/Grafana-Dashboards-ff8800?logo=grafana)

## Executive Summary
**Air4Campus** is a lightweight IoT system designed to detect and monitor rapid changes in **temperature, humidity, and indoor gas concentration** in university classrooms. ESP32-based sensor nodes send real-time readings to a Flask backend, which stores all data in MongoDB (Atlas or local).  
The system supports public deployment through Render, real-time dashboards in Grafana, and can be extended with alerting features for safety or anomaly detection.

---

## Objectives
- Measure and store indoor **temperature, humidity, and gas concentration** using sensors such as **MQ135** and **DHT11**.  
- Provide HTTP endpoints to insert and retrieve sensor data.
- Offer a simple test interface using a web form.
- Support both local execution (via Docker or Python) and cloud deployment with Render.
- Visualize system data through **Grafana dashboards**.
- Enable future alerting systems (SMS, email, mobile notifications).

---

## Hardware (Sensors)

| Sensor | Measures | Communication | Notes |
|--------|----------|---------------|-------|
| **MQ-135** | Gas concentration (approx. air quality) | Analog | Slow response but useful trend indicator |
| **DHT11** | Temperature (°C), Humidity (%) | Digital | Simple and reliable for indoor use |
| **ESP32** | Host microcontroller | WiFi | Sends JSON via HTTP |

Each device sends a JSON payload containing:

- `device_id`: unique device identifier  
- `temperature`: `{ value, unit }`  
- `humidity`: `{ value, unit }`  
- `air_quality`: `{ value, unit }`  
- `ts`: timestamp (optional; generated if missing)  
- `meta`: optional metadata (location, notes, etc.)

---

## System Architecture

### Simple Diagram (ASCII)

```
ESP32 ──> Flask API ──> MongoDB Atlas ──> Grafana
```

---

## Tech Stack
- Python 3.8+  
- Flask  
- MongoDB / MongoDB Atlas  
- pymongo, dnspython, MicroPython
- Docker + docker-compose (optional)  
- Render (cloud hosting)

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/receive_sensor_data` | Insert new sensor reading |
| `GET`  | `/json_api_data` | List stored readings |

---

## Data Flow
1. The ESP32 sends JSON data to `/receive_sensor_data`.  
2. Flask validates and timestamps the payload.  
3. MongoDB stores the data in the `data` collection.  
4. Grafana visualizes real-time values and trends.

---

## Example Document Schema
```json
{
  "device_id": "esp32_lab01",
  "temperature": { "value": 26, "unit": "C" },
  "humidity": { "value": 49, "unit": "%" },
  "air_quality": { "value": 0, "unit": "ratio" },
  "ts": "2025-11-21T18:28:50Z"
}
```

---

## Environment Variables
Create a `.env` or add them in Render:

```ini
MONGO_URL=mongodb+srv://USER:PASS@cluster.mongodb.net/air4campus
MONGO_DB=air4campus
FLASK_ENV=production
PORT=7001
```

### `.env.example`
```env
# MongoDB Atlas connection
MONGO_URL=

# Database name
MONGO_DB=air4campus

# Flask settings
FLASK_ENV=development
PORT=7001
```

---

## Running Locally (Without Docker)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r src/requirements.txt
export MONGO_URL='mongodb+srv://USER:PASS@cluster.mongodb.net/air4campus'
cd src
python3 app.py
```

Visit: http://localhost:7001/test-form

---

## Running with Docker
```bash
docker-compose up --build -d
docker-compose logs -f web
```

Backend at: http://localhost:7001

---

## Sending Data (curl)
```bash
curl -X POST http://localhost:7001/api/data   -H "Content-Type: application/json"   -d '{
        "device_id":"esp32_lab01",
        "temperature":{"value":26,"unit":"C"},
        "humidity":{"value":49,"unit":"%"},
        "air_quality":{"value":0,"unit":"ratio"}
      }'
```

---

## Deployment on Render
1. Create a Web Service.
2. Add environment variables.
3. Configure Python build.
4. Allow Render IP in Atlas (or temporarily open access for testing).

---

## Grafana Dashboards (Example Views)
- Temperature time-series  
- Humidity long-term trend  
- Air-quality fluctuations (MQ135)  
- Threshold-based anomalies  
- Classroom comparison panels

---

## Future Improvements
- Mobile/email alerts for sudden changes  
- Classroom location mapping  
- Multi-device aggregation  
- Predictive trends using ML  
- Better calibration of MQ135

---

## License

This project is licensed under the Apache License 2.0.

See the LICENSE file for details.
