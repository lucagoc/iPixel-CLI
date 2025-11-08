"""Set brightness command producing a SendPlan instead of raw bytes."""

from ..lib.convert import to_int, validate_range, int_to_hex
from ..lib.transport.send_plan import single_window_plan

def set_brightness(value):
    """Return a SendPlan to set the brightness."""
    value = to_int(value, "brightness")
    validate_range(value, 0, 100, "Brightness")
    payload = bytes.fromhex("05000480") + bytes.fromhex(int_to_hex(value))
    return single_window_plan("set_brightness", payload, requires_ack=True)
