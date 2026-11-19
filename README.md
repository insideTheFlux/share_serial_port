# Share a serial port over the network

`share_serial_port.py` lets a computer on your network use a serial port that is plugged into a different computer.
It is one small Python file. It needs only Python 3 and the `pyserial` package.

I wrote it to work on a DM-32UV radio (running [RadioFoundry](https://github.com/RadioFoundry/RadioFoundry)) that is
plugged into a Windows laptop by its programming cable, while the tools and tests ran on a Linux computer. Nothing in
it is specific to that radio: it passes bytes between a serial port and a network connection, using the standard
RFC 2217 ("telnet serial port") protocol.

## How it works

```
 Linux computer (tools)  ──── network ────  Windows laptop (this script)  ──── cable ────  radio
 rfc2217://LAPTOP-IP:7001                   share_serial_port.py COM3 7001
```

The computer with the radio runs the script. The other computer connects to it and uses the port as if the radio
were plugged in locally. Only one client can be connected at a time. When it disconnects, the script waits for the
next one.

## What you need

- Python 3 and `pyserial` on the computer that has the radio: `python -m pip install pyserial`
- Both computers on the same network, with the laptop's address known (`ipconfig` on Windows, `ip a` on Linux)
- The serial port's name: on Windows, a `COM` number (Device Manager > Ports); on Linux, usually `/dev/ttyUSB0`

## Step by step

1. Plug the radio's cable into the computer that will share it.
2. On that computer, start the script with the port name and a TCP port number (7001 is just an example):

       python share_serial_port.py COM3 7001

   It prints `sharing COM3 on tcp port 7001; Ctrl+C stops`. On Windows, if the firewall asks, allow it on the
   private network only.
3. On the other computer, give the tools the address `rfc2217://LAPTOP-IP:7001` wherever they take a serial port.
   With the RadioFoundry tools:

       python3 tools/rfoundry_debug.py --port rfc2217://LAPTOP-IP:7001 version
       python3 -m pytest tests/hil --radio-port rfc2217://LAPTOP-IP:7001

   Any program that uses pyserial can open the same address with `serial.serial_for_url("rfc2217://LAPTOP-IP:7001", 115200)`.
4. When you are done, stop the script with Ctrl+C.

## Safety

**There is no password and no encryption.** The script listens on every network interface, so anything that can
reach the port can use the radio, including keying a transmitter if the tools you run allow it. Use it only on a
network you trust, keep the firewall rule to the private network, and stop the script when you finish.

## If something goes wrong

| What you see | Likely cause |
|---|---|
| `No module named 'serial'` | pyserial isn't installed: `python -m pip install pyserial` |
| The script exits asking for `DEVICE TCP_PORT` | You started it without the port name and TCP port, for example `python share_serial_port.py COM3 7001` |
| `No route to host` or no answer from the other computer | Wrong IP address, a different network or VLAN, the laptop asleep, or a firewall blocking port 7001 |
| `Remote does not seem to support RFC2217` | The address isn't this script (or it crashed): check the script's window and restart it |
| Connected, but the radio doesn't answer | The radio was restarted or its cable replugged after the script started. Stop the script (Ctrl+C) and start it again |
| `Could not open port` on the radio's computer | Another program has the port open, or the COM number is wrong. Close the other program, or check Device Manager |

## Status and limits

- Tried with a DM-32UV's programming cable between a Windows laptop and a Linux computer: the debug link answered
  and one HIL test passed through it.
- This tidied version (renamed and commented) was not rerun against a radio. It was only syntax-checked, and
  an earlier copy of the same logic was the one that ran.
- One client at a time. If the cable is unplugged while the script runs, it does not recover: restart it.

## License

MIT, copied from RadioFoundry together with its `AUTHORS` file. The copyright line in the script header is
RadioFoundry's and stays. See `LICENSE` and [FORKING.md](https://github.com/RadioFoundry/RadioFoundry/blob/main/FORKING.md).
