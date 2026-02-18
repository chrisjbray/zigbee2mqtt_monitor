#!/usr/bin/env python3
import argparse
import json
import logging
import os
import sys
import time
from collections import defaultdict
from datetime import datetime
from threading import Lock

import paho.mqtt.client as mqtt

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Argument Parsing
parser = argparse.ArgumentParser(description="Zigbee2MQTT Network Traffic Monitor")
parser.add_argument(
    "--host", default=os.getenv("MQTT_SERVER", "127.0.0.1"), help="MQTT Server"
)
parser.add_argument(
    "--port", type=int, default=int(os.getenv("MQTT_PORT", 1883)), help="MQTT Port"
)
parser.add_argument("--user", default=os.getenv("MQTT_USER", ""), help="MQTT User")
parser.add_argument(
    "--password", default=os.getenv("MQTT_PASSWORD", ""), help="MQTT Password"
)
parser.add_argument(
    "--base-topic", default="zigbee2mqtt", help="Base Z2M topic (default: zigbee2mqtt)"
)
parser.add_argument(
    "--interval", type=int, default=5, help="Reporting interval in seconds"
)
parser.add_argument(
    "--ignore-bridge", action="store_true", help="Ignore bridge/ topics"
)
parser.add_argument(
    "--detail", type=int, default=1, help="Topic depth to show (default: 1)"
)
args = parser.parse_args()

# Stats tracking
stats_lock = Lock()
topic_stats = defaultdict(lambda: {"count": 0, "bytes": 0, "last_seen": 0})
total_messages = 0
total_bytes = 0
start_time = time.time()


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logger.info(f"Connected to MQTT broker at {args.host}")
        sub_topic = f"{args.base_topic}/#"
        client.subscribe(sub_topic)
        logger.info(f"Subscribed to {sub_topic}")
    else:
        logger.error(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    global total_messages, total_bytes
    topic = msg.topic

    if args.ignore_bridge and f"{args.base_topic}/bridge" in topic:
        return

    # Extract device name based on detail level
    parts = topic.split("/")
    # Detail level 1: bridge, my_device
    # Detail level 2: bridge/logging, bridge/state, my_device/availability
    depth = min(len(parts), args.detail + 1)
    device = "/".join(parts[1:depth])
    if not device:
        device = topic

    payload_size = len(msg.payload)

    with stats_lock:
        total_messages += 1
        total_bytes += payload_size
        topic_stats[device]["count"] += 1
        topic_stats[device]["bytes"] += payload_size
        topic_stats[device]["last_seen"] = time.time()


def format_bytes(size):
    temp_size = size
    for unit in ["B", "KB", "MB"]:
        if temp_size < 1024:
            return f"{temp_size:7.2f} {unit}"
        temp_size /= 1024
    return f"{temp_size:7.2f} GB"


def format_rate(bytes_per_sec):
    # Byte rate (KB/s)
    temp_bytes = bytes_per_sec
    byte_unit = "B/s"
    if temp_bytes >= 1024:
        temp_bytes /= 1024
        byte_unit = "KB/s"
    if temp_bytes >= 1024:
        temp_bytes /= 1024
        byte_unit = "MB/s"

    # Bit rate (kbps) - bits use 1000 as divisor
    temp_bits = bytes_per_sec * 8
    bit_unit = "bps"
    if temp_bits >= 1000:
        temp_bits /= 1000
        bit_unit = "kbps"
    if temp_bits >= 1000:
        temp_bits /= 1000
        bit_unit = "Mbps"

    return f"{temp_bytes:7.2f} {byte_unit} ({temp_bits:7.2f} {bit_unit})"


def print_report():
    os.system("clear")
    now = time.time()
    elapsed = now - start_time

    # Get terminal size
    try:
        columns, lines = os.get_terminal_size()
    except OSError:
        columns, lines = 80, 24

    with stats_lock:
        current_stats = list(topic_stats.items())
        mps = total_messages / elapsed
        bps = total_bytes / elapsed
        total_msg = total_messages
        total_sz = total_bytes

    # Sort by message count descending
    current_stats.sort(key=lambda x: x[1]["count"], reverse=True)

    print(
        f"Zigbee2MQTT Network Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(
        f"Elapsed: {elapsed:0.1f}s | Total Msg: {total_msg} ({mps:0.2f}/s) | Total Data: {format_bytes(total_sz)} | Rate: {format_rate(bps)}"
    )
    print("-" * columns)
    print(
        f"{'Device/Topic':<40} | {'Messages':<10} | {'Data Volume':<12} | {'Last Seen'}"
    )
    print("-" * columns)

    # Calculate how many rows we can fit (headers are 5 lines, footer might be 1)
    max_rows = lines - 6
    if max_rows < 1:
        max_rows = 1

    for device, data in current_stats[:max_rows]:
        last_seen_str = f"{now - data['last_seen']:0.1f}s ago"
        print(
            f"{device[:40]:<40} | {data['count']:<10} | {format_bytes(data['bytes']):<12} | {last_seen_str}"
        )

    if not current_stats:
        print("Waiting for messages...")


# Client Setup
try:
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
except (AttributeError, TypeError):
    client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

if args.user and args.password:
    client.username_pw_set(args.user, args.password)

try:
    client.connect(args.host, args.port, 60)
    client.loop_start()

    while True:
        print_report()
        time.sleep(args.interval)

except KeyboardInterrupt:
    print("\nStopping monitor...")
except Exception as e:
    logger.error(f"Error: {e}")
finally:
    client.loop_stop()
    client.disconnect()
