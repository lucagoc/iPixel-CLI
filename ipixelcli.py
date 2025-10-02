import json
import asyncio
import argparse
import websockets
from bleak import BleakClient
from commands import *

COMMANDS = {
    "clear": clear,
    "set_brightness": set_brightness,
    "set_clock_mode": set_clock_mode,
    "set_rhythm_mode": set_rhythm_mode,
    "set_rhythm_mode_2": set_rhythm_mode_2,
    "set_time": set_time,
    "set_fun_mode": set_fun_mode,
    "set_pixel": set_pixel,
    "delete_screen": delete_screen,
    "send_text": send_text,
    "set_speed" : set_speed,
    "send_animation": send_animation,
    "set_orientation": set_orientation,
    "send_png": send_png,
    "led_on": led_on,
    "led_off": led_off
}

# Socket server
async def handle_websocket(websocket, address):
    async with BleakClient(address) as client:
        print("[INFO] Connected to the device")
        try:
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
                        positional_args = []
                        keyword_args = {}
                        for param in params:
                            if "=" in param:
                                key, value = param.split("=", 1)
                                keyword_args[key.replace('-', '_')] = value
                            else:
                                positional_args.append(param)

                        # Generate the data to send
                        data = COMMANDS[command_name](*positional_args, **keyword_args)

                        # Send the data to the device
                        await client.write_gatt_char(
                            "0000fa02-0000-1000-8000-00805f9b34fb", data
                        )

                        # Prepare the response
                        response = {"status": "success", "command": command_name}
                    else:
                        response = {"status": "error", "message": "Commande inconnue"}
                except Exception as e:
                    response = {"status": "error", "message": str(e)}

                # Send the response to the client
                await websocket.send(json.dumps(response))
        except websockets.ConnectionClosed:
            print("[INFO] Websocket connection has been closed")

async def start_server(ip, port, address):
    server = await websockets.serve(lambda ws: handle_websocket(ws, address), ip, port)
    print(f"WebSocket server started on ws://{ip}:{port}")
    await server.wait_closed()

def build_command_args(params):
    positional_args = []
    keyword_args = {}
    for param in params:
        if "=" in param:
            key, value = param.split("=", 1)
            keyword_args[key.replace('-', '_')] = value
        else:
            positional_args.append(param)
    return positional_args, keyword_args

async def run_multiple_commands(commands, address):
    async with BleakClient(address) as client:
        print("[INFO] Connected to the device")
        for cmd in commands:
            command_name = cmd[0]
            params = cmd[1:]
            if command_name in COMMANDS:
                positional_args, keyword_args = build_command_args(params)
                data = COMMANDS[command_name](*positional_args, **keyword_args)
                await client.write_gatt_char("0000fa02-0000-1000-8000-00805f9b34fb", data)
                print(f"[INFO] Command '{command_name}' executed successfully.")
            else:
                print(f"[ERROR] Unknown command: {command_name}")

async def execute_command(command_name, params, address):
    async with BleakClient(address) as client:
        print("[INFO] Connected to the device")
        if command_name in COMMANDS:
            positional_args, keyword_args = build_command_args(params)
            data = COMMANDS[command_name](*positional_args, **keyword_args)
            await client.write_gatt_char("0000fa02-0000-1000-8000-00805f9b34fb", data)
            print(f"[INFO] Command '{command_name}' executed successfully.")
        else:
            print(f"[ERROR] Unknown command: {command_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebSocket BLE Server")
    parser.add_argument("-s", "--server", action="store_true", help="Run as WebSocket server")
    parser.add_argument("-p", "--port", type=int, default=4444, help="Specify the port for the server")
    parser.add_argument(
        "-c", "--command", action="append", nargs="+", metavar="COMMAND PARAMS",
        help="Execute a specific command with parameters. Can be used multiple times."
    )
    parser.add_argument("-a", "--address", required=True, help="Specify the Bluetooth device address")

    args = parser.parse_args()

    if args.server:
        asyncio.run(start_server("localhost", args.port, args.address))
    elif args.command:
        asyncio.run(run_multiple_commands(args.command, args.address))
    else:
        print("[ERROR] No mode specified. Use --server or -c with -a to specify an address.")
