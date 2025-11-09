"""
Get device information command.
"""

import logging
from datetime import datetime

from ..lib.device_info import parse_device_info, DeviceInfo
from ..lib.transport.send_plan import single_window_plan

logger = logging.getLogger(__name__)


def build_get_device_info_command() -> bytes:
    """Build the get device info command payload.
    
    Command format: [8, 0, 1, 128, hour, minute, second, language]
    
    Returns:
        Command bytes to send to the device.
    """
    now = datetime.now()
    cmd = bytes([
        8,                 # Command header
        0,                 # Reserved
        1,                 # Sub-command
        0x80,              # -128 in signed byte
        now.hour,          # Current hour
        now.minute,        # Current minute
        now.second,        # Current second
        0,                 # Language (0 for default)
    ])
    return cmd


async def _handle_device_info_response(client, response: bytes) -> DeviceInfo:
    """Parse the device info response.
    
    Args:
        client: BleakClient (unused but required by response_handler signature).
        response: Raw response bytes from the device.
        
    Returns:
        Parsed DeviceInfo object.
    """
    logger.debug(f"Parsing device info response: {response.hex()}")
    return parse_device_info(response)


def get_device_info():
    """Return a SendPlan for requesting device information.
    
    This command includes a response_handler, so send_plan() will automatically
    capture and parse the response.
    
    Returns:
        A SendPlan with response handling for device info.
    """
    payload = build_get_device_info_command()
    return single_window_plan(
        "get_device_info",
        payload,
        requires_ack=False,
        response_handler=_handle_device_info_response
    )
