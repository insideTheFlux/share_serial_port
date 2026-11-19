#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The RadioFoundry Authors
"""Share one serial port over the network (RFC 2217), one client at a time. Needs only pyserial.

For a radio on a machine other than the one running the tools: plug the radio's cable in there, run this, and point
the tools on the other machine at it, for example

    python3 share_serial_port.py COM3 7001                    (the machine with the radio)
    python3 tools/rfoundry_debug.py --port rfc2217://HOST:7001 version
    python3 -m pytest tests/hil --radio-port rfc2217://HOST:7001

There is no password: it listens on every network interface, so anything that can reach the port can use the radio.
Run it only on a network you trust, and stop it (Ctrl+C) when done.
"""
import socket
import sys
import threading

import serial
import serial.rfc2217


def serve(dev, tcp_port):
    ser = serial.serial_for_url(dev, 115200, timeout=1)
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", tcp_port))
    srv.listen(1)
    print(f"sharing {dev} on tcp port {tcp_port}; Ctrl+C stops", flush=True)
    while True:
        conn, addr = srv.accept()
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        print("client", addr, flush=True)

        class Conn:                   # PortManager writes its replies to an object with write()
            def write(self, data):
                conn.sendall(data)

        pm = serial.rfc2217.PortManager(ser, Conn())
        alive = [True]

        def to_net():
            while alive[0]:
                try:
                    d = ser.read(ser.in_waiting or 1)
                    if d:
                        conn.sendall(b"".join(pm.escape(d)))
                except Exception:
                    break

        t = threading.Thread(target=to_net, daemon=True)
        t.start()
        try:
            while True:
                d = conn.recv(1024)
                if not d:
                    break
                ser.write(b"".join(pm.filter(d)))
        except Exception:
            pass
        alive[0] = False
        t.join(2)
        conn.close()
        print("client gone", flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: share_serial_port.py DEVICE TCP_PORT   (DEVICE: COM3, /dev/ttyUSB0)")
    try:
        serve(sys.argv[1], int(sys.argv[2]))
    except KeyboardInterrupt:
        pass
