"""Set brightness command producing a SendPlan instead of raw bytes."""

from ..lib.convert import to_int, validate_range, int_to_hex
from ..lib.transport.send_plan import single_window_plan

def set_brightness(level: int):
    """Return a SendPlan to set the brightness."""
    if (0 > int(level)) or (int(level) > 100):
        raise ValueError("Brightness level must be between 0 and 100")
    payload = bytes([
        5,          # Command header
        0,          # Reserved
        4,          # sub-command
        0x80,       # param
        int(level)  # brightness value
    ])
    return single_window_plan("set_brightness", payload)
