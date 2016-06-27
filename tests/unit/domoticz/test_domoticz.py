# -*- coding: utf-8 -*-
import pytest
import subprocess
import requests_mock

from domoticz.domoticz import is_ip_device_present, is_ip_device_awol, json_api_filter_parameters


def test_should_tell_ip_device_is_present(monkeypatch):
    def call(*args, **kwargs):
        return 0
    monkeypatch.setattr(subprocess, 'call', call)
    assert is_ip_device_present(None) is True
    assert is_ip_device_awol(None) is False


def test_should_tell_ip_device_is_awol(monkeypatch):
    def call(*args, **kwargs):
        return 2
    monkeypatch.setattr(subprocess, 'call', call)
    assert is_ip_device_present(None) is False
    assert is_ip_device_awol(None) is True


def test_should_remove_null_values_from_parameters():
    params = dict(a=1, b='two', c=None, d=4.56)
    filtered = json_api_filter_parameters(params)
    assert sorted(filtered.keys()) == ['a', 'b', 'd']


def test():
    with requests_mock.mock() as m:
        m.get('http://192.168.0.91:8080/json.htm', text='data')
