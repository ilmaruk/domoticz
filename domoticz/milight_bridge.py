# -*- coding: utf-8 -*-
import socket
import time

ON_COMMANDS = [
    bytearray([0x42, 0x00]),
    bytearray([0x45, 0x00]),
    bytearray([0x47, 0x00]),
    bytearray([0x49, 0x00]),
    bytearray([0x4B, 0x00]),
]
OFF_COMMANDS = [
    bytearray([0x41, 0x00]),
    bytearray([0x46, 0x00]),
    bytearray([0x48, 0x00]),
    bytearray([0x4A, 0x00]),
    bytearray([0x4C, 0x00]),
]
WHITE_COMMANDS = [None, 0xC5, 0xC7, 0xC9, 0xD1]

COLOR_GREEN = bytearray([0xC0, 0x60])
COLOR_RED = bytearray([0xC0, 0xB0])


class MiLightError(Exception):
    pass


def with_switch_on(func):
    def decorator(self, *args, **kwargs):
        if kwargs.get('switch_on', False):
            self.switch_on(args[0])
        func(self, *args, **kwargs)
    return decorator


class MiLightBridge(object):
    def __init__(self, bridge_ip, bridge_port):
        self._bridge_ip = bridge_ip
        self._bridge_port = bridge_port

    def _send(self, data, duration=0):
        try:
            family, type, proto, canon_name, sock_addr = socket.getaddrinfo(self._bridge_ip, self._bridge_port)[0]
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            returned = sock.sendto(data, (sock_addr[0], sock_addr[1]))
            sock.close()
            del sock
            # Sleep at least 100 msecs
            time.sleep(max(duration, 0.1))
        except Exception as error:
            raise MiLightError(error.message)

    def switch_on(self, group, duration=0):
        self._send(ON_COMMANDS[group], duration)

    def switch_off(self, group, duration=0):
        self._send(OFF_COMMANDS[group], duration)

    @with_switch_on
    def set_color(self, group, color, duration=0, switch_on=False):
        self._send(color, duration)

    @with_switch_on
    def set_white(self, group, duration=0, switch_on=False):
        self._send(bytearray([WHITE_COMMANDS[group], 0x00]), duration)
