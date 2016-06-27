# -*- coding: utf-8 -*-
import logging
from domoticz.milight_bridge import MiLightBridge, COLOR_RED, COLOR_GREEN

logging.basicConfig(level=logging.DEBUG)

bridge = MiLightBridge('192.168.0.93', '8899')
logging.info('Turning off for one second')
bridge.switch_off(2, 1)
logging.info('Setting color to Red for one second')
bridge.set_color(2, COLOR_RED, duration=1, switch_on=True)
logging.info('Setting color to Green for one second')
bridge.set_color(2, COLOR_GREEN, 1)
logging.info('Setting color to White')
bridge.set_white(2)
