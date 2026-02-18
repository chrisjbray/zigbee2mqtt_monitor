# Zigbee2MQTT Network Monitor

Identify noisy devices and monitor overall network utilization by analyzing MQTT traffic.

## Development Rules

- **Formatting:** Use `black` for all Python code formatting.
- **Environment:** Use the shared virtual environment located in the parent directory: `../venv/`.
- **Tracking:** Keep the `TODO.md` file updated with progress and remaining tasks.

## Key Logic

- **Traffic Ingestion:** Subscribes to `zigbee2mqtt/#`.
- **Aggregation:** Calculates message counts and data volume (bytes) per device/topic.
- **Reporting:** Displays a live "Top Talkers" table, dynamically sized to the terminal height.
- **Rate Units:** Displays data rates in the format `XX KB/s (YYY kbps)`.
