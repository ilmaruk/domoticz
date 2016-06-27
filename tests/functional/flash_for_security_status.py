# -*- coding: utf-8 -*-
import logging
from domoticz.json_api_client import JsonApiClient, DEVICE_STATUS_ON, DEVICE_STATUS_OFF
from domoticz.milight_bridge import MiLightBridge, COLOR_RED

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

json_api_client = JsonApiClient('http://192.168.0.91:8080')
milight_bridge = MiLightBridge('192.168.0.93', '8899')

device_status = json_api_client.get_device_status(27)
logging.info('Device status is: {status:s}'.format(status=device_status))

alternate_command = getattr(milight_bridge, 'set_white') if device_status == DEVICE_STATUS_ON \
    else getattr(milight_bridge, 'switch_off')
for _ in range(1, 5):
    logging.info('Setting color to Red')
    milight_bridge.set_color(2, COLOR_RED, duration=.5, switch_on=device_status==DEVICE_STATUS_OFF)
    logging.info('Re-setting color')
    alternate_command(2, duration=.5)

device_status = json_api_client.get_device_status(27)
logging.info('Device status is: {status:s}'.format(status=device_status))

if device_status == DEVICE_STATUS_OFF:
    milight_bridge.switch_off(2)
else:
    milight_bridge.set_white(2, switch_on=True)
