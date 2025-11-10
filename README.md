# HDFury API Client

An **asynchronous Python client** for communicating with **HDFury devices** via their HTTP API.
This lightweight library provides methods for fetching device information, configuration, and issuing control commands such as reboot, hotplug, and mode changes.

## Features

* Asynchronous communication using `aiohttp`
* Fetch device information and configuration
* Issue control commands (reboot, hotplug, relay, mute, etc.)
* Built-in error handling for connection and parsing failures
* Designed for easy integration into automation tools or async workflows

## Requirements

* Python **3.11+**
* `aiohttp` library

## Usage Example

```python
import asyncio
from hdfury import HDFuryAPI, HDFuryError

async def main():
    client = HDFuryAPI("192.168.1.100")  # Replace with your device IP

    try:
        info = await client.get_info()
        print("Device Info:", info)

        board = await client.get_board()
        print("Board Info:", board)

        config = await client.get_config()
        print("Configuration:", config)

        # Example command: reboot the device
        await client.issue_reboot()
        print("Reboot command sent!")

    except HDFuryError as err:
        print(f"Error communicating with HDFury device: {err}")

    finally:
        await client.close()

asyncio.run(main())
```

## API Reference

### Class: `HDFuryAPI`

#### Initialization

```python
HDFuryAPI(host: str, session: aiohttp.ClientSession | None = None)
```

* **host** – IP address or hostname of the HDFury device.
* **session** *(optional)* – existing `aiohttp.ClientSession` to reuse.

#### Fetch Methods

| Method         | Description                                   |
|----------------|-----------------------------------------------|
| `get_board()`  | Get board information (`/ssi/brdinfo.ssi`)    |
| `get_info()`   | Get general device info (`/ssi/infopage.ssi`) |
| `get_config()` | Get configuration data (`/ssi/confpage.ssi`)  |

#### Command Methods

| Method                                                    | Description                    |
|-----------------------------------------------------------|--------------------------------|
| `issue_reboot()`                                          | Reboot the device              |
| `issue_hotplug()`                                         | Trigger HDMI hotplug           |
| `set_operation_mode(mode)`                                | Set device operation mode      |
| `set_port_selection(tx0, tx1)`                            | Set device HDMI port selection |
| `set_auto_switch_inputs(state)`                           | Toggle auto input switching    |
| `set_htpc_mode_rx0(state)` → `set_htpc_mode_rx3(state)`   | Set HTPC mode per input        |
| `set_mute_tx0_audio(state)` → `set_mute_tx1_audio(state)` | Mute/unmute TX audio           |
| `set_oled(state)`                                         | Control OLED display           |
| `set_ir_active(state)`                                    | Enable/disable IR              |
| `set_relay(state)`                                        | Control relay state            |

#### Cleanup

```python
await client.close()
```

Closes any open HTTP sessions.

## Exception Handling

All exceptions inherit from `HDFuryError`.

| Exception               | Description                                               |
|-------------------------|-----------------------------------------------------------|
| `HDFuryError`           | Base exception for the HDFury client                      |
| `HDFuryConnectionError` | Connection-related errors (timeouts, bad responses, etc.) |
| `HDFuryParseError`      | Raised when JSON decoding fails                           |

## Constants

### `OPERATION_MODES`

Defined in [`const.py`](src/hdfury/const.py), this dictionary maps known operation mode identifiers to their human-readable descriptions.

```python
from hdfury import OPERATION_MODES

for mode, description in OPERATION_MODES.items():
    print(f"{mode}: {description}")
```

| Key   | Description                            |
|-------|----------------------------------------|
| `"0"` | Mode 0 - Splitter TX0/TX1 FRL5 VRR     |
| `"1"` | Mode 1 - Splitter TX0/TX1 UPSCALE FRL5 |
| `"2"` | Mode 2 - Matrix TMDS                   |
| `"3"` | Mode 3 - Matrix FRL→TMDS               |
| `"4"` | Mode 4 - Matrix DOWNSCALE              |
| `"5"` | Mode 5 - Matrix RX0:FRL5 + RX1-3:TMDS  |

These can be used to display or interpret the current operating mode returned by the device.

## License

MIT
