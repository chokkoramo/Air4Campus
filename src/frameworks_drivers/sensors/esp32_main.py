import dht
import machine
import network
import time
import ujson
import urequests

from dht11_reader import DHT11Reader
from esp32_payload import ESP32PayloadBuilder
from mq135_reader import MQ135Reader


WIFI_SSID = "TU_RED_WIFI"
WIFI_PASSWORD = "TU_PASSWORD_WIFI"
API_URL = "http://TU_SERVIDOR:7001/receive_sensor_data"

DEVICE_ID = "esp32_aula_01"
CLASSROOM_ID = "aula_101"
CLASSROOM_TYPE = "theoretical"

DHT11_PIN = 14
MQ135_ADC_PIN = 33
READ_INTERVAL_SECONDS = 30


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    while not wlan.isconnected():
        time.sleep(1)


def create_sensor_readers():
    dht_sensor = dht.DHT11(machine.Pin(DHT11_PIN))
    mq135_adc = machine.ADC(machine.Pin(MQ135_ADC_PIN))
    mq135_adc.atten(machine.ADC.ATTN_11DB)

    return DHT11Reader(dht_sensor), MQ135Reader(mq135_adc)


def send_payload(payload):
    response = urequests.post(
        API_URL,
        data=ujson.dumps(payload),
        headers={"Content-Type": "application/json"},
    )
    response.close()


def main():
    connect_wifi()
    dht11_reader, mq135_reader = create_sensor_readers()
    payload_builder = ESP32PayloadBuilder(
        device_id=DEVICE_ID,
        classroom_id=CLASSROOM_ID,
        classroom_type=CLASSROOM_TYPE,
    )

    while True:
        readings = [
            dht11_reader.read(),
            mq135_reader.read(),
        ]
        send_payload(payload_builder.build(readings))
        time.sleep(READ_INTERVAL_SECONDS)


main()
