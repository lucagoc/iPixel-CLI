"""
# pypixelcolor cli.py
Command-line interface for iPixel BLE commands
"""

import asyncio
import argparse
import logging
from bleak import BleakClient, BleakScanner

from .lib.logging import setup_logging
from .lib.transport.send_plan import send_plan
from .lib.transport.ack_manager import AckManager
from .websocket import build_command_args
from .commands import COMMANDS

NOTIFY_UUID = "0000fa03-0000-1000-8000-00805f9b34fb"

logger = logging.getLogger(__name__)


async def run_multiple_commands(commands, address):
    """Execute multiple BLE commands sequentially.
    
    Args:
        commands: List of command tuples (command_name, *params).
        address: Bluetooth device address.
    """
    async with BleakClient(address) as client:
        logger.info("Connected to the device")
        # Enable notify-based ACKs
        ack_mgr = AckManager()
        try:
            await client.start_notify(NOTIFY_UUID, ack_mgr.make_notify_handler())
        except Exception as e:
            logger.warning(f"Failed to enable notifications on {NOTIFY_UUID}: {e}")
        for cmd in commands:
            command_name = cmd[0]
            params = cmd[1:]
            if command_name in COMMANDS:
                positional_args, keyword_args = build_command_args(params)
                plan = COMMANDS[command_name](*positional_args, **keyword_args)
                await send_plan(client, plan, ack_mgr)
                logger.info(f"Command '{command_name}' executed successfully.")
            else:
                logger.error(f"Unknown command: {command_name}")
        try:
            await client.stop_notify(NOTIFY_UUID)
        except Exception:
            pass


async def execute_command(command_name, params, address):
    """Execute a single BLE command.
    
    Args:
        command_name: Name of the command to execute.
        params: List of parameters for the command.
        address: Bluetooth device address.
    """
    async with BleakClient(address) as client:
        logger.info("Connected to the device")
        # Enable notify-based ACKs
        ack_mgr = AckManager()
        try:
            await client.start_notify(NOTIFY_UUID, ack_mgr.make_notify_handler())
        except Exception as e:
            logger.warning(f"Failed to enable notifications on {NOTIFY_UUID}: {e}")
        if command_name in COMMANDS:
            positional_args, keyword_args = build_command_args(params)
            plan = COMMANDS[command_name](*positional_args, **keyword_args)
            await send_plan(client, plan, ack_mgr)
            logger.info(f"Command '{command_name}' executed successfully.")
        else:
            logger.error(f"Unknown command: {command_name}")
        try:
            await client.stop_notify(NOTIFY_UUID)
        except Exception:
            pass


async def scan_devices():
    """Scan for Bluetooth devices with 'LED' in their name."""
    logger.info("Scanning for Bluetooth devices...")
    devices = await BleakScanner.discover()
    if devices:
        led_devices = [device for device in devices if device.name and "LED" in device.name]
        logger.info(f"Found {len(led_devices)} device(s):")
        for device in led_devices:
            logger.info(f"  - {device.name} ({device.address})")
    else:
        logger.info("No Bluetooth devices found.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="iPixel CLI - BLE Command Tool")
    parser.add_argument("--scan", action="store_true", help="Scan for Bluetooth devices")
    parser.add_argument(
        "-c", "--command", action="append", nargs="+", metavar="COMMAND PARAMS",
        help="Execute a specific command with parameters. Can be used multiple times."
    )
    parser.add_argument("-a", "--address", help="Specify the Bluetooth device address")
    parser.add_argument("--noemojis", action="store_true", help="Disable emojis in log output")

    args = parser.parse_args()
    
    setup_logging(use_emojis=not args.noemojis)

    if args.scan:
        asyncio.run(scan_devices())
    elif args.command:
        if not args.address:
            logger.error("--address is required when using --command")
            exit(1)
        asyncio.run(run_multiple_commands(args.command, args.address))
    else:
        logger.error("No mode specified. Use --scan or -c with -a to specify an address.")
        logger.info("For WebSocket server mode, use: python -m pypixelcolor.websocket -a <address>")


if __name__ == "__main__":
    main()
