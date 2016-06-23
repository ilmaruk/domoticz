#!/usr/bin/python
#   Title: check_device_online.py
#   Author: Chopper_Rob
#   Date: 25-02-2015
#   Info: Checks the presence of the given device on the network and reports back to domoticz
#   URL : https://www.chopperrob.nl/domoticz/5-report-devices-online-status-to-domoticz
#   Version : 1.6.2

import sys
import datetime
import time
import os
import subprocess
import urllib2
import base64

import logging
import requests

# Settings for the domoticz server
from domoticz.domoticz import get_ip_device_presence

domoticz_server = "192.168.0.91:8080"
domoticz_username = ""
domoticz_password = ""
domoticz_passcode = "20Gioele14"
domoticz_credentials = (domoticz_username, domoticz_password)

# If enabled. The script will log to the file _.log
# Logging to file only happens after the check for other instances, before that it only prints to screen.
log_to_file = False

# The script supports two types to check if another instance of the script is running.
# One will use the ps command, but this does not work on all machine (Synology has problems)
# The other option is to create a pid file named _.pid. The script will update the timestamp
# every interval. If a new instance of the script spawns it will check the age of the pid file.
# If the file doesn't exist or it is older then 3 * Interval it will keep running, otherwise is stops.
# Please chose the option you want to use "ps" or "pid", if this option is kept empty it will not check and just run.
check_for_instances = "pid"

VIRTUAL_DEVICE_STATUS_ON = 'On'
VIRTUAL_DEVICE_STATUS_OFF = 'Off'
MOBILE_STATUS_UNKNOWN = -1
MOBILE_STATUS_ONLINE = 0
MOBILE_STATUS_OFFLINE = 2

# DO NOT CHANGE BEYOND THIS LINE
if len(sys.argv) != 5:
    print ("Not enough parameters. Needs %Host %Switchid %Interval %Cooldownperiod.")
    sys.exit(0)

device = sys.argv[1]
switchid = sys.argv[2]
interval = sys.argv[3]
cooldownperiod = sys.argv[4]
previousstate = -1
lastsuccess = datetime.datetime.now()
lastreported = -1
base64string = base64.encodestring('%s:%s' % (domoticz_username, domoticz_password)).replace('\n', '')
domoticz_url = 'http://' + domoticz_server + '/json.htm?type=devices&filter=all&used=true&order=Name'

if check_for_instances.lower() == "pid":
    pidfile = sys.argv[0] + '_' + sys.argv[1] + '.pid'
    if os.path.isfile(pidfile):
        print datetime.datetime.now().strftime("%H:%M:%S") + "- pid file exists"
        if (time.time() - os.path.getmtime(pidfile)) < (float(interval) * 3):
            print datetime.datetime.now().strftime("%H:%M:%S") + "- script seems to be still running, exiting"
            print datetime.datetime.now().strftime(
                "%H:%M:%S") + "- If this is not correct, please delete file " + pidfile
            sys.exit(0)
        else:
            print datetime.datetime.now().strftime("%H:%M:%S") + "- Seems to be an old file, ignoring."
    else:
        open(pidfile, 'w').close()

if check_for_instances.lower() == "ps":
    if int(subprocess.check_output('ps x | grep \'' + sys.argv[0] + ' ' + sys.argv[1] + '\' | grep -cv grep',
                                   shell=True)) > 2:
        print (datetime.datetime.now().strftime("%H:%M:%S") + "- script already running. exiting.")
        sys.exit(0)


def log(message):
    message = datetime.datetime.now().strftime("%H:%M:%S") + "- " + message
    print message
    if log_to_file is True:
        logfile = open(sys.argv[0] + '_' + sys.argv[1] + '.log', "a")
        logfile.write(message + "\n")
        logfile.close()


def domoticz_get_status(default=VIRTUAL_DEVICE_STATUS_OFF):
    logging.info('Getting virtual device status ...')
    response = requests.get(domoticz_url, auth=domoticz_credentials)
    response.raise_for_status()
    data = response.json()
    status = default
    if data["status"] == "OK":
        for i, v in enumerate(data["result"]):
            if data["result"][i]["idx"] == switchid:
                status = data["result"][i]["Status"]
                break
    logging.info('Virtual device status is {status:s}'.format(status=status))
    return status


def domoticz_set_status(switch_id, switch_cmd):
    params = {
        'type': 'command',
        'param': 'switchlight',
        'idx': switch_id,
        'switchcmd': switch_cmd,
        'level': 0,
        'passcode': domoticz_passcode
    }
    response = requests.get("http://" + domoticz_server + "/json.htm",
                            params=params, auth=domoticz_credentials)
    response.raise_for_status()


def domoticz_request(url):
    request = urllib2.Request(url)
    request.add_header("Authorization", "Basic %s" % base64string)
    response = urllib2.urlopen(request)
    return response.read()


def main():
    logging.info('Script started')

    last_reported = domoticz_get_status()

    previous_mobile_status = MOBILE_STATUS_UNKNOWN
    while True:
        logging.info('Checking mobile status ...')
        current_state = get_ip_device_presence(device)
        logging.debug(str(current_state))

        if current_state == 0:
            last_success = datetime.datetime.now()
            if current_state != previous_mobile_status and last_reported == VIRTUAL_DEVICE_STATUS_ON:
                log(device + " online, no need to tell domoticz")
            elif current_state != previous_mobile_status and last_reported != VIRTUAL_DEVICE_STATUS_ON:
                if domoticz_get_status() == VIRTUAL_DEVICE_STATUS_OFF:
                    logging.info(device + " is online; tell domoticz it's back")
                    domoticz_set_status(switchid, VIRTUAL_DEVICE_STATUS_ON)
                else:
                    log(device + " online, but domoticz already knew")
                last_reported = 1

        elif current_state != previous_mobile_status:
            log(device + " offline, waiting for it to come back")

            if (datetime.datetime.now() - last_success).total_seconds() > float(
                    cooldownperiod) and last_reported != VIRTUAL_DEVICE_STATUS_OFF:
                if domoticz_get_status() == VIRTUAL_DEVICE_STATUS_ON:
                    logging.info(device + " is offline; tell domoticz it's gone")
                    domoticz_set_status(switchid, VIRTUAL_DEVICE_STATUS_OFF)
                else:
                    log(device + " offline, but domoticz already knew")
                last_reported = 0

        time.sleep(float(interval))

        previous_mobile_status = current_state
        if check_for_instances.lower() == "pid":
            open(pidfile, 'w').close()


def logging_setup():
    logging.basicConfig(format='[%(asctime)s] %(levelname)s - %(message)s', level=logging.DEBUG)

if '__main__' == __name__:
    logging_setup()
    sys.exit(main())
