# Air4Campus - Sistema IoT para monitoreo de calidad del aire

![Estado](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Licencia](https://img.shields.io/badge/license-Apache%202.0-lightgrey)
![Render](https://img.shields.io/badge/Deploy-Render-orange)
![Grafana](https://img.shields.io/badge/Grafana-Dashboards-ff8800?logo=grafana)

## Resumen

Air4Campus es un sistema IoT liviano para monitorear condiciones ambientales en aulas. Los nodos ESP32 leen temperatura, humedad y calidad del aire, envían los datos a una API Flask, y la API guarda lecturas normalizadas en MongoDB para dashboards, consultas y análisis de confort.

El backend soporta MongoDB local, MongoDB Atlas, Docker Compose, despliegue en Render y dashboards de Grafana mediante endpoints compatibles con JSON.

## Funcionalidades principales

- Recibe lecturas de sensores desde dispositivos ESP32 por HTTP.
- Soporta lecturas de temperatura/humedad con DHT11 y calidad del aire con MQ135.
- Acepta el payload moderno con arreglo `sensors` y el formato anterior con campos anidados.
- Normaliza la hora antes de guardar los datos en MongoDB.
- Guarda `ts` como fecha nativa de MongoDB y `timestamp_ms` como Unix epoch en milisegundos.
- Genera la hora en el servidor si el dispositivo no la envía.
- Calcula el estado de confort del aula: `optimal`, `regular` o `critical`.
- Produce recomendaciones y alertas cuando las condiciones están fuera de rango.
- Expone endpoints para lecturas recientes y consultas de series de tiempo tipo Grafana.
- Puede ejecutarse localmente con Python o Docker Compose.

## Hardware

| Componente | Propósito | Notas |
| --- | --- | --- |
| ESP32 | Microcontrolador con Wi-Fi | Envía payloads JSON a la API Flask |
| DHT11 | Temperatura y humedad | Sensor simple para interiores |
| MQ135 | Tendencia de calidad del aire | Sensor analógico de gases; útil para cambios relativos |

## Arquitectura

```text
ESP32 -> API Flask -> MongoDB Atlas/MongoDB local -> Grafana/clientes API
```

El código está organizado por capas:

- `entities`: modelos de dominio y reglas de confort del aula.
- `use_cases`: flujos de aplicación para recibir, consultar y analizar lecturas.
- `interface_adapters`: controladores Flask, presentadores JSON y adaptadores de payloads de sensores.
- `frameworks_drivers`: MongoDB, configuración de Flask y código MicroPython del ESP32.

## Endpoints del API

| Método | Endpoint | Descripción |
| --- | --- | --- |
| `GET` | `/` | Health check. Responde `OK`. |
| `POST` | `/receive_sensor_data` | Guarda una lectura y retorna el análisis de confort. |
| `GET`/`POST` | `/json_api_data` | Retorna lecturas recientes. Acepta filtros opcionales `sensor` y `limit`. |
| `POST` | `/search` | Retorna etiquetas de sensores disponibles para dashboards. |
| `POST` | `/query` | Retorna puntos de series de tiempo en formato compatible con Grafana. |

## Payload de sensores

Formato recomendado:

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

También se acepta el formato anterior:

```json
{
  "device_id": "esp32_lab01",
  "temperature": { "value": 26, "unit": "C" },
  "humidity": { "value": 49, "unit": "%" },
  "air_quality": { "value": 420, "unit": "ppm" }
}
```

## Manejo de hora y timestamp

La API acepta varios nombres de campo para que el firmware del ESP32 y otros clientes puedan cambiar sin romper el backend:

- `ts`
- `timestamp`
- `timestamp_ms`
- `timestampMs`
- `timesnap`
- `time`
- `hora`
- `fecha`

Formatos aceptados:

- Texto ISO 8601, por ejemplo `2025-11-21T18:28:50Z`.
- Unix epoch en segundos, por ejemplo `1763749730`.
- Unix epoch en milisegundos, por ejemplo `1763749730000`.
- Textos numéricos con epoch en segundos o milisegundos.

MongoDB guarda:

- `ts`: fecha UTC normalizada de MongoDB, usada para ordenar y consultar rangos de tiempo.
- `timestamp_ms`: Unix epoch numérico en milisegundos, útil para clientes frontend y depuración.

Si no se envía ninguna hora, Flask usa la hora UTC de recepción del servidor.

## Forma del documento en MongoDB

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
    "recommendations": ["Aumentar renovacion de aire."],
    "alerts": []
  }
}
```

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto o configura estas variables en Render:

```env
MONGO_URL=mongodb+srv://USER:PASS@cluster.mongodb.net/air4campus
MONGO_DB=air4campus
FLASK_ENV=development
PORT=7001
```

Para usar MongoDB local con Docker:

```env
MONGO_URL=mongodb://admin:admin123@mongo:27017/air4campus?authSource=admin
MONGO_DB=air4campus
```

## Ejecutar localmente con Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt
export MONGO_URL="mongodb://localhost:27017/"
export MONGO_DB="air4campus"
cd src
python app.py
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r src\requirements.txt
$env:MONGO_URL = "mongodb://localhost:27017/"
$env:MONGO_DB = "air4campus"
Set-Location src
python app.py
```

La API queda disponible en `http://localhost:7001`.

## Ejecutar con Docker Compose

```bash
docker-compose up --build -d
docker-compose logs -f web
```

Servicios:

- API Flask: `http://localhost:7001`
- MongoDB: `localhost:27017`
- Mongo Express: `http://localhost:8081`
- Grafana: `http://localhost:3000`

## Enviar una lectura

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

Respuesta de ejemplo:

```json
{
  "ok": true,
  "id": "656000000000000000000000",
  "ts": 1763749730000,
  "comfort": {
    "status": "regular",
    "recommendations": ["Aumentar renovacion de aire."],
    "alerts": []
  }
}
```

## Consultar datos recientes

```bash
curl "http://localhost:7001/json_api_data?sensor=temperature&limit=20"
```

Filtros válidos para `sensor`:

- `temperature`
- `humidity`
- `air_quality`

Si no se envía `sensor`, el endpoint retorna documentos completos recientes.

## Integración con Grafana

El proyecto incluye endpoints que pueden ser consumidos por plugins de fuente de datos JSON en Grafana:

- `/search` para descubrir métricas.
- `/query` para valores de series de tiempo.
- `/json_api_data` para lecturas recientes sin procesar.

Paneles típicos:

- Temperatura en el tiempo.
- Humedad relativa en el tiempo.
- Tendencia de calidad del aire con MQ135.
- Estado de confort por aula.
- Alertas críticas y recomendaciones.

## Firmware ESP32

Los archivos MicroPython del ESP32 están en `src/frameworks_drivers/sensors`.

Archivos importantes:

- `main.py`: conexión Wi-Fi, ciclo de sensores y POST HTTP.
- `config.example.py`: plantilla de configuración del firmware.
- `dht11_reader.py`: lector del DHT11.
- `mq135_reader.py`: lector del MQ135.
- `esp32_payload.py`: constructor del payload.

El backend puede asignar la hora automáticamente, así que el ESP32 no necesita RTC para enviar datos válidos.

## Despliegue en Render

1. Crea un Web Service en Render.
2. Conecta este repositorio.
3. Usa `src` como directorio de la aplicación si es necesario.
4. Instala dependencias desde `src/requirements.txt`.
5. Configura `MONGO_URL`, `MONGO_DB` y `FLASK_ENV`.
6. Permite el acceso de red de Render en MongoDB Atlas.

## Mejoras futuras

- Enviar alertas reales por correo, SMS o notificaciones push.
- Agregar autenticación para endpoints de escritura.
- Agregar pruebas automatizadas para adaptadores de payload y reglas de confort.
- Crear índices de MongoDB para despliegues con más datos.
- Mejorar la calibración del MQ135 por aula.
- Agregar mapas de aulas y gestión de dispositivos.

## Licencia

Este proyecto está licenciado bajo Apache License 2.0. Consulta `LICENSE` para más detalles.
