# -*- coding: utf-8 -*-
import logging
import sys
import time
import datetime
import yaml
import threading

from domoticz.domoticz import IP_DEVICE_PRESENT, get_ip_device_presence, IP_DEVICE_UNKNOWN_STATUS, \
    set_virtual_device_status


def worker(device_info, domoticz_config):
    device_ip = device_info['ip']
    latest_status = IP_DEVICE_UNKNOWN_STATUS
    is_awol = False
    awol_started = None
    while True:
        virtual_device_status = None
        current_status = get_ip_device_presence(device_ip)
        is_present = current_status == IP_DEVICE_PRESENT

        if is_present and latest_status != current_status:
            is_awol = False
            awol_started = None
            virtual_device_status = 'On'
        elif not is_present:
            if awol_started is None:
                awol_started = datetime.datetime.now()

            awol_duration = (datetime.datetime.now() - awol_started).total_seconds()
            if awol_duration < device_info['awol_threshold']:
                logging.info('Device {device_ip:s} is not present, but not yet flagged AWOL'.
                             format(device_ip=device_ip))
            elif not is_awol:
                logging.info('Device {device_ip:s} is now AWOL'.format(device_ip=device_ip))
                is_awol = True
                virtual_device_status = 'Off'
            else:
                logging.info('Device {device_ip:s} has been AWOL for {seconds:d} seconds'.
                             format(device_ip=device_ip, seconds=int(awol_duration)))

        if virtual_device_status is not None:
            set_virtual_device_status(device_info['device_idx'], virtual_device_status, domoticz_config['passcode'])

        latest_status = current_status

        time.sleep(device_info['polling_interval'])

    return 0


def main(config):
    for device in config['devices']:
        threading.Thread(target=worker, args=(device, config['domoticz'])).start()


def setup_logging():
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s - %(message)s')


def read_configuration():
    with open('check_ip_device_presence.yaml') as stream:
        config = yaml.load(stream)
    return config

if '__main__' == __name__:
    setup_logging()
    config = read_configuration()
    try:
        sys.exit(main(config))
    except Exception as error:
        print error
        sys.exit(2)
