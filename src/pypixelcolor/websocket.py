"""
# pypixelcolor websocket.py
WebSocket server for BLE communication
"""

import json
import logging
import argparse
import websockets
from bleak import BleakClient

from .lib.logging import setup_logging
from .lib.transport.send_plan import send_plan
from .lib.transport.ack_manager import AckManager
from .commands import COMMANDS

logger = logging.getLogger(__name__)

NOTIFY_UUID = "0000fa03-0000-1000-8000-00805f9b34fb"

def build_command_args(params):
    """Parse command parameters into positional and keyword arguments."""
    positional_args = []
    keyword_args = {}
    for param in params:
        if "=" in param:
            key, value = param.split("=", 1)
            keyword_args[key.replace('-', '_')] = value
        else:
            positional_args.append(param)
    return positional_args, keyword_args


async def handle_websocket(websocket, address):
    """Handle WebSocket connections and execute BLE commands."""
    async with BleakClient(address) as client:
        logger.info("Connected to the device")
        try:
            # Enable notify-based ACKs for flow control
            ack_mgr = AckManager()
            try:
                await client.start_notify(NOTIFY_UUID, ack_mgr.make_notify_handler())
            except Exception as e:
                logger.warning(f"Failed to enable notifications on {NOTIFY_UUID}: {e}")
            
            while True:
                # Wait for a message from the client
                message = await websocket.recv()

                # Parse JSON
                try:
                    command_data = json.loads(message)
                    command_name = command_data.get("command")
                    params = command_data.get("params", [])

                    if command_name in COMMANDS:
                        # Separate positional and keyword arguments
                        positional_args, keyword_args = build_command_args(params)

                        # Build the SendPlan (or wrap legacy bytes to plan)
                        plan = COMMANDS[command_name](*positional_args, **keyword_args)
                        await send_plan(client, plan, ack_mgr)

                        # Prepare the response
                        response = {"status": "success", "command": command_name}
                    else:
                        response = {"status": "error", "message": "Commande inconnue"}
                except Exception as e:
                    response = {"status": "error", "message": str(e)}

                # Send the response to the client
                await websocket.send(json.dumps(response))
        except websockets.ConnectionClosed:
            logger.info("Websocket connection has been closed")
        finally:
            try:
                await client.stop_notify(NOTIFY_UUID)
            except Exception:
                pass


async def start_server(ip, port, address):
    """Start the WebSocket server."""
    server = await websockets.serve(lambda ws: handle_websocket(ws, address), ip, port)
    logger.info(f"WebSocket server started on ws://{ip}:{port}")
    await server.wait_closed()


if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description="WebSocket BLE Server")
    parser.add_argument("-p", "--port", type=int, default=4444, help="Specify the port for the server")
    parser.add_argument("--host", default="localhost", help="Bind address (e.g., 0.0.0.0, ::, or localhost)")
    parser.add_argument("-a", "--address", required=True, help="Specify the Bluetooth device address")
    parser.add_argument("--noemojis", action="store_true", help="Disable emojis in log output")
    
    args = parser.parse_args()
    
    setup_logging(use_emojis=not args.noemojis)
    
    import asyncio
    asyncio.run(start_server(args.host, args.port, args.address))
