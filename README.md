# Zigbee2MQTT Network Monitor

A real-time CLI tool to identify noisy devices and monitor overall network utilization on your Zigbee network by analyzing MQTT traffic.

## Features

- **Live Top Talkers:** View a sorted list of devices sending the most messages.
- **Bandwidth Analysis:** Track data volume (KB/s) per device to find heavy payloads.
- **Network Statistics:** Monitor overall messages per second and total data throughput.
- **Granular Reporting:** Use the `--detail` flag to dive into sub-topics (e.g., `bridge/logging`).
- **Topic Filtering:** Optionally ignore Zigbee2MQTT bridge noise to focus solely on device chatter.

## Prerequisites

- Python 3.x
- Access to a Zigbee2MQTT MQTT broker.

## Setup

It is recommended to use the shared virtual environment located in the parent directory:

```bash
# Install dependencies (if not already done)
../venv/bin/pip install -r requirements.txt
```

## Usage

Run the monitor with your MQTT broker credentials:

```bash
../venv/bin/python monitor.py --host <broker_ip> --user <username> --password <password>
```

### CLI Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--host` | `127.0.0.1` | MQTT Broker hostname or IP. |
| `--port` | `1883` | MQTT Broker port. |
| `--user` | (None) | MQTT Username. |
| `--password` | (None) | MQTT Password. |
| `--base-topic` | `zigbee2mqtt` | The base topic used by your Z2M instance. |
| `--interval` | `5` | How often to refresh the CLI report (seconds). |
| `--detail` | `1` | Depth of topics to show (1 = device name, 2 = sub-topics). |
| `--ignore-bridge`| `False` | Hide all `bridge/` internal messages. |

## Example

To see which devices are chatty while ignoring bridge logs:

```bash
../venv/bin/python monitor.py --host <broker_ip> --user <username> --password <password> --ignore-bridge
```
