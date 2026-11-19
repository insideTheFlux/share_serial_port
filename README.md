# serial-rfc2217-relay

Shares one serial port over the network (RFC 2217), one client at a time. It needs only Python 3 and pyserial.
Use it to reach a radio that is plugged into another computer, for example a radio on a Windows laptop while the
tools run on a Linux machine.

On the machine with the radio:

    python -m pip install pyserial
    python serial_rfc2217_relay.py COM3 7001          # Linux: /dev/ttyUSB0

On the other machine, use the port URL `rfc2217://HOST:7001` wherever a serial port is accepted, for example with
the RadioFoundry tools:

    python3 tools/rfoundry_debug.py --port rfc2217://HOST:7001 version
    python3 -m pytest tests/hil --radio-port rfc2217://HOST:7001

**There is no password.** The relay listens on every network interface, so anything that can reach the port can use
the radio. Run it only on a network you trust, and stop it (Ctrl+C) when you are done.

Status: tried with a DM-32UV's programming cable between a Windows laptop and a Linux machine (debug link and one
HIL test). The tidied version in this repository was not rerun against a radio. One client at a time; no reconnect
handling for a cable that is unplugged while the relay runs.

The script comes from [RadioFoundry](https://github.com/RadioFoundry/RadioFoundry) and keeps its MIT license
(`LICENSE`), its `AUTHORS` file and the copyright line in the script header.
