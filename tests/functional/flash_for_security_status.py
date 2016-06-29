# -*- coding: utf-8 -*-
import logging
import ledcontroller
import time

from domoticz.json_api_client import JsonApiClient, DEVICE_STATUS_ON, DEVICE_STATUS_OFF

LIGHTS_GROUP = 2
INTERVALS = .15
LOOPS = 3

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

json_api_client = JsonApiClient('http://192.168.0.91:8080')
led_controller = ledcontroller.LedController('192.168.0.93')

security_status = json_api_client.get_device_status(8)
logging.info('Security status is: {status:s}'.format(status=security_status))
if security_status == 'Arm Home':
    logging.info('Nothing to do')
flashing_color = 'green' if security_status == 'Normal' else 'red'

device_status = json_api_client.get_device_status(27)
logging.info('Device status is: {status:s}'.format(status=device_status))

if device_status == DEVICE_STATUS_OFF:
    led_controller.on(LIGHTS_GROUP)

for _ in range(1, LOOPS+1):
    led_controller.set_color(flashing_color, LIGHTS_GROUP)
    time.sleep(INTERVALS)
    if device_status == DEVICE_STATUS_OFF:
        led_controller.off(LIGHTS_GROUP)
    else:
        led_controller.white(LIGHTS_GROUP)
    time.sleep(INTERVALS)

device_status = json_api_client.get_device_status(27)
logging.info('Device status is: {status:s}'.format(status=device_status))

led_controller.white(LIGHTS_GROUP)
if device_status == DEVICE_STATUS_OFF:
    led_controller.off(LIGHTS_GROUP)
