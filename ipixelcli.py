import json
import asyncio
import argparse
import websockets
import logging
from bleak import BleakClient, BleakScanner
from commands import *
import bit_tools

class EmojiFormatter(logging.Formatter):
    EMOJI_MAP = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔥'
    }
    
    def format(self, record):
        emoji = self.EMOJI_MAP.get(record.levelname, '📝')
        record.levelname = f"{emoji}"
        return super().format(record)

def setup_logging(use_emojis=True):
    log_format = '%(levelname)s [%(asctime)s] [%(name)s] %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    if use_emojis:
        formatter = EmojiFormatter(log_format, datefmt=date_format)
    else:
        formatter = logging.Formatter(log_format, datefmt=date_format)
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    logging.basicConfig(level=logging.INFO, handlers=[handler])

logger = logging.getLogger(__name__)

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
        logger.info("Connected to the device")
        try:
            # Enable notify-based ACKs for flow control
            ack_mgr = BleAckManager()
            try:
                await client.start_notify(NOTIFY_UUID, _make_notify_handler(ack_mgr))
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

                        # Send using windowed GIF sender for GIF commands, else chunked
                        if command_name in ("send_animation"):
                            await send_gif_windowed(client, data, ack_mgr)
                        else:
                            await send_chunked(client, data, ack_mgr)

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
    server = await websockets.serve(lambda ws: handle_websocket(ws, address), ip, port)
    logger.info(f"WebSocket server started on ws://{ip}:{port}")
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
        logger.info("Connected to the device")
        # Enable notify-based ACKs
        ack_mgr = BleAckManager()
        try:
            await client.start_notify(NOTIFY_UUID, _make_notify_handler(ack_mgr))
        except Exception as e:
            logger.warning(f"Failed to enable notifications on {NOTIFY_UUID}: {e}")
        for cmd in commands:
            command_name = cmd[0]
            params = cmd[1:]
            if command_name in COMMANDS:
                positional_args, keyword_args = build_command_args(params)
                data = COMMANDS[command_name](*positional_args, **keyword_args)
                if command_name in ("send_animation"):
                    await send_gif_windowed(client, data, ack_mgr)
                else:
                    await send_chunked(client, data, ack_mgr)
                logger.info(f"Command '{command_name}' executed successfully.")
            else:
                logger.error(f"Unknown command: {command_name}")
        try:
            await client.stop_notify(NOTIFY_UUID)
        except Exception:
            pass

async def execute_command(command_name, params, address):
    async with BleakClient(address) as client:
        logger.info("Connected to the device")
        # Enable notify-based ACKs
        ack_mgr = BleAckManager()
        try:
            await client.start_notify(NOTIFY_UUID, _make_notify_handler(ack_mgr))
        except Exception as e:
            logger.warning(f"Failed to enable notifications on {NOTIFY_UUID}: {e}")
        if command_name in COMMANDS:
            positional_args, keyword_args = build_command_args(params)
            data = COMMANDS[command_name](*positional_args, **keyword_args)
            if command_name in ("send_animation"):
                await send_gif_windowed(client, data, ack_mgr)
            else:
                await send_chunked(client, data, ack_mgr)
            logger.info(f"Command '{command_name}' executed successfully.")
        else:
            logger.error(f"Unknown command: {command_name}")
        try:
            await client.stop_notify(NOTIFY_UUID)
        except Exception:
            pass

async def scan_devices():
    logger.info("Scanning for Bluetooth devices...")
    devices = await BleakScanner.discover()
    if devices:
        led_devices = [device for device in devices if device.name and "LED" in device.name]
        logger.info(f"Found {len(led_devices)} device(s):")
        for device in led_devices:
            logger.info(f"  - {device.name} ({device.address})")
    else:
        logger.info("No Bluetooth devices found.")

# Replace ipixelcli import with local helpers
from bit_tools import get_frame_size

WRITE_UUID = "0000fa02-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000fa03-0000-1000-8000-00805f9b34fb"

class BleAckManager:
    def __init__(self):
        self.window_event = asyncio.Event()
        self.all_event = asyncio.Event()

    def reset(self):
        self.window_event.clear()
        self.all_event.clear()


def _make_notify_handler(ack_mgr: BleAckManager):
    def handler(_, data: bytes):
        if not data:
            return
        try:
            logging.getLogger(__name__).debug(f"Notify frame: {data.hex()}")
        except Exception:
            pass
        if len(data) == 5 and data[0] == 0x05:
            if data[4] in (0, 1):
                ack_mgr.window_event.set()
            elif data[4] == 3:
                ack_mgr.window_event.set()
                ack_mgr.all_event.set()
            return
        b0 = data[0]
        b4 = data[4] if len(data) > 4 else None
        if b0 == 0x05 and b4 is not None:
            if b4 in (0, 1):
                ack_mgr.window_event.set()
            elif b4 == 3:
                ack_mgr.window_event.set()
                ack_mgr.all_event.set()
    return handler


def _parse_gif_transport(data: bytes):
    """Parse single-frame GIF transport payload built by commands.py.
    Format: [len_hi,len_lo] 0x03 0x00 0x00 <size:4 LE> <crc:4 LE> 0x02 0x01 <gif_bytes>
    Returns dict with size_bytes, crc_bytes, tail_bytes, gif_bytes, or None if not GIF.
    """
    if len(data) < 2 + 13:
        return None
    offset = 2  # skip 2-byte length prefix
    if data[offset] != 0x03 or data[offset + 1] != 0x00:
        return None
    option_byte = data[offset + 2]
    size_bytes = data[offset + 3: offset + 7]
    crc_bytes = data[offset + 7: offset + 11]
    if data[offset + 11] != 0x02 or data[offset + 12] != 0x01:
        return None
    tail_bytes = data[offset + 11: offset + 13]
    gif_len = int.from_bytes(size_bytes, "little")
    gif_start = offset + 13
    if gif_start + gif_len > len(data):
        return None
    gif_bytes = data[gif_start: gif_start + gif_len]
    return {
        "option": option_byte,
        "size_bytes": size_bytes,
        "crc_bytes": crc_bytes,
        "tail_bytes": tail_bytes,
        "gif_bytes": gif_bytes,
    }


def _length_prefix(frame_len: int) -> bytes:
    """Return 2-byte big-endian length prefix equal to (frame_len + 2)."""
    total = frame_len + 2
    return total.to_bytes(2, "big")


async def send_gif_windowed(client, data: bytes, ack_mgr: BleAckManager, *, chunk_size: int = 244, window_size: int = 12 * 1024, ack_timeout: float = 8.0):
    parsed = _parse_gif_transport(data)
    if not parsed:
        await send_chunked(client, data, ack_mgr, chunk_size=chunk_size, window_size=window_size, ack_timeout=ack_timeout)
        return

    gif = parsed["gif_bytes"]
    size_bytes = parsed["size_bytes"]
    crc_bytes = parsed["crc_bytes"]

    pos = 0
    ack_mgr.reset()
    window_index = 0
    while pos < len(gif):
        window_end = min(pos + window_size, len(gif))
        chunk_payload = gif[pos:window_end]
        option = 0x00 if window_index == 0 else 0x02
        serial = 0x01 if window_index == 0 else 0x65
        cur_tail = bytes([0x02, serial])
        header = bytes([0x03, 0x00, option]) + size_bytes + crc_bytes + cur_tail
        frame = header + chunk_payload
        prefix_hex = get_frame_size("FFFF" + frame.hex(), 4)
        try:
            prefix = bytes.fromhex(prefix_hex)
        except Exception:
            prefix = _length_prefix(len(frame))
        message = prefix + frame

        ack_mgr.window_event.clear()
        logging.getLogger(__name__).debug(f"Window {window_index}: option={option}, serial={serial}, prefix={prefix.hex()}, header={header.hex()[:32]}...")

        wpos = 0
        while wpos < len(message):
            wend = min(wpos + chunk_size, len(message))
            await client.write_gatt_char(WRITE_UUID, message[wpos:wend], response=True)
            wpos = wend

        try:
            await asyncio.wait_for(ack_mgr.window_event.wait(), timeout=ack_timeout)
        except asyncio.TimeoutError:
            raise RuntimeError("cur12k_no_answer: no ack from device")

        window_index += 1
        pos = window_end

    try:
        await asyncio.wait_for(ack_mgr.all_event.wait(), timeout=ack_timeout)
    except asyncio.TimeoutError:
        pass


async def send_chunked(client, data: bytes, ack_mgr: BleAckManager, *, chunk_size: int = 244, window_size: int = 12 * 1024, ack_timeout: float = 8.0):
    total = len(data)
    pos = 0
    ack_mgr.reset()
    while pos < total:
        window_end = min(pos + window_size, total)
        ack_mgr.window_event.clear()
        while pos < window_end:
            end = min(pos + chunk_size, window_end)
            chunk = data[pos:end]
            await client.write_gatt_char(WRITE_UUID, chunk, response=True)
            pos = end
        try:
            await asyncio.wait_for(ack_mgr.window_event.wait(), timeout=ack_timeout)
        except asyncio.TimeoutError:
            raise RuntimeError("cur12k_no_answer: no ack from device")
    try:
        await asyncio.wait_for(ack_mgr.all_event.wait(), timeout=ack_timeout)
    except asyncio.TimeoutError:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebSocket BLE Server")
    parser.add_argument("-s", "--server", action="store_true", help="Run as WebSocket server")
    parser.add_argument("--scan", action="store_true", help="Scan for Bluetooth devices")
    parser.add_argument("-p", "--port", type=int, default=4444, help="Specify the port for the server")
    parser.add_argument(
        "-c", "--command", action="append", nargs="+", metavar="COMMAND PARAMS",
        help="Execute a specific command with parameters. Can be used multiple times."
    )
    parser.add_argument("--host", default="localhost", help="Bind address (e.g., 0.0.0.0, ::, or localhost)")
    parser.add_argument("-a", "--address", help="Specify the Bluetooth device address")
    parser.add_argument("--noemojis", action="store_true", help="Disable emojis in log output")

    args = parser.parse_args()
    
    setup_logging(use_emojis=not args.noemojis)

    if args.scan:
        asyncio.run(scan_devices())
    elif args.server:
        if not args.address:
            logger.error("--address is required when using --server")
            exit(1)
        asyncio.run(start_server(args.host, args.port, args.address))
    elif args.command:
        if not args.address:
            logger.error("--address is required when using --command")
            exit(1)
        asyncio.run(run_multiple_commands(args.command, args.address))
    else:
        logger.error("No mode specified. Use --scan, --server or -c with -a to specify an address.")