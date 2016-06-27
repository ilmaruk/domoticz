# -*- coding: utf-8 -*-
import pytest
import requests_mock
import json

from domoticz.json_api_client import JsonApiClient, DEVICE_STATUS_OFF, JsonApiError

TEST_HOST = 'http://server/'


@pytest.fixture
def sut():
    return JsonApiClient(TEST_HOST)


@pytest.fixture
def response_body():
    return {
        "ActTime": 1467058024,
        "ServerTime": "2016-06-27 21:07:04",
        "Sunrise": "04:39",
        "Sunset": "21:24",
        "result": [],
        "status": "OK",
        "title": "Devices"
    }


@pytest.fixture
def device():
    return {
        "AddjMulti": 1.0,
        "AddjMulti2": 1.0,
        "AddjValue": 0.0,
        "AddjValue2": 0.0,
        "BatteryLevel": 255,
        "CustomImage": 0,
        "Data": "Off",
        "Description": "",
        "Favorite": 1,
        "HardwareID": 4,
        "HardwareName": "Mi-Light WiFi Interface",
        "HardwareType": "Limitless/AppLamp/Mi Light with LAN/WiFi interface",
        "HardwareTypeVal": 22,
        "HaveDimmer": True,
        "HaveGroupCmd": False,
        "HaveTimeout": False,
        "ID": "1",
        "Image": "Light",
        "IsSubDevice": False,
        "LastUpdate": "2016-06-27 19:51:51",
        "Level": 0,
        "LevelInt": 0,
        "MaxDimLevel": 100,
        "Name": "Outside Lights",
        "Notifications": "False",
        "PlanID": "0",
        "PlanIDs": [0],
        "Protected": False,
        "ShowNotifications": True,
        "SignalLevel": "-",
        "Status": "Off",
        "StrParam1": "",
        "StrParam2": "",
        "SubType": "RGBW",
        "SwitchType": "On/Off",
        "SwitchTypeVal": 0,
        "Timers": "False",
        "Type": "Lighting Limitless/Applamp",
        "TypeImg": "lightbulb",
        "Unit": 2,
        "Used": 1,
        "UsedByCamera": False,
        "XOffset": "0",
        "YOffset": "0",
        "idx": "27"
    }


def test_should_get_device_status(sut, response_body, device):
    response_body['result'].append(device)
    with requests_mock.Mocker() as m:
        m.get(TEST_HOST + 'json.htm?type=devices&rid=1', text=json.dumps(response_body))
        status = sut.get_device_status(1)
        assert status == DEVICE_STATUS_OFF


def test_should_raise_an_error(sut):
    with requests_mock.Mocker() as m:
        m.get(TEST_HOST + 'json.htm?type=devices&rid=1', status_code=567)
        with pytest.raises(JsonApiError) as error:
            sut.get_device_status(1)
        assert error.value.message.startswith('567')
