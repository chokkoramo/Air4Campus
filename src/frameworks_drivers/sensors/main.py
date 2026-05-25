import dht
import machine
import network
import time
import ujson
import urequests

from config import (
    API_URL,
    CLASSROOM_ID,
    CLASSROOM_TYPE,
    DEVICE_ID,
    DHT11_PIN,
    MQ135_ADC_PIN,
    MQ135_CONVERSION_FACTOR,
    READ_INTERVAL_SECONDS,
    WIFI_PASSWORD,
    WIFI_SSID,
)
from dht11_reader import DHT11Reader
from esp32_payload import ESP32PayloadBuilder
from mq135_reader import MQ135Reader


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print("Conectando a la red Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
            
    print("Wi-Fi conectado. IP:", wlan.ifconfig()[0])
    return wlan


def create_sensor_readers():
    dht_sensor = dht.DHT11(machine.Pin(DHT11_PIN))
    mq135_adc = machine.ADC(machine.Pin(MQ135_ADC_PIN))
    mq135_adc.atten(machine.ADC.ATTN_11DB)

    return DHT11Reader(dht_sensor), MQ135Reader(mq135_adc, MQ135_CONVERSION_FACTOR)


def send_payload(payload):
    response = None
    try:
        response = urequests.post(
            API_URL,
            data=ujson.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        print("Respuesta API:", response.status_code, response.text)
    finally:
        if response is not None:
            response.close()


def main():
    wlan = connect_wifi()
    dht11_reader, mq135_reader = create_sensor_readers()
    payload_builder = ESP32PayloadBuilder(
        device_id=DEVICE_ID,
        classroom_id=CLASSROOM_ID,
        classroom_type=CLASSROOM_TYPE,
    )

    while True:
        if not wlan.isconnected():
            print("Conexión perdida. Intentando reconectar...")
            wlan = connect_wifi()
            
        try:
            dht_data = dht11_reader.read()
            mq135_data = mq135_reader.read()
            
            print("--- Nuevas Lecturas ---")
            print(f"DHT11: {dht_data}")
            print(f"MQ135: {mq135_data}")
            print("-----------------------")
            
            readings = [dht_data, mq135_data]
            send_payload(payload_builder.build(readings))
            print("Datos enviados con éxito al servidor.\n")
            
        except OSError as exc:
            if exc.args[0] == 116:
                print("Error de Timeout (116): El sensor o la red tardaron demasiado.\n")
            else:
                print(f"Error de red/hardware: {exc}\n")
                
        except Exception as exc:
            print(f"Sensor loop error inesperado: {exc}\n")

        time.sleep(READ_INTERVAL_SECONDS)


main()
