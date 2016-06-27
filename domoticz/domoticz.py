# -*- coding: utf-8 -*-
import subprocess
import logging

import requests

IP_DEVICE_UNKNOWN_STATUS = -1
IP_DEVICE_PRESENT = 0
IP_DEVICE_AWOL = 2


def get_ip_device_presence(device_ip):
    logging.info('Getting presence for IP device {device_ip:s}'.format(device_ip=device_ip))
    command = 'ping -q -c1 -W 1 {device_ip:s} > /dev/null'.format(device_ip=device_ip)
    return subprocess.call(command, shell=True)


def is_ip_device_present(device_ip):
    return get_ip_device_presence(device_ip) == IP_DEVICE_PRESENT


def is_ip_device_awol(device_ip):
    return get_ip_device_presence(device_ip) == IP_DEVICE_AWOL


def set_virtual_device_status(virtual_device_idx, status, domoticz_passcode=None):
    params = {
        'type': 'command',
        'param': 'switchlight',
        'idx': virtual_device_idx,
        'switchcmd': status,
        'level': 0,
        'passcode': domoticz_passcode
    }
    response = requests.get("http://192.168.0.91:8080/json.htm",
                            params=params)
    response.raise_for_status()


def json_api_request(**params):
    response = requests.get("http://192.168.0.91:8080/json.htm", params=params)
    response.raise_for_status()
    return response


def json_api_filter_parameters(params):
    return {key: value for (key, value) in params.items() if value is not None}


def json_api_get_all_devices(type='devices', filter='all', used=None, order='Name'):
    params = dict(type=type, filter=filter, used=used, order=order)
    response = json_api_request(**json_api_filter_parameters(params))
