# -*- coding: utf-8 -*-
import pytest
import subprocess

from domoticz.domoticz import is_ip_device_present, is_ip_device_awol


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
