from ..lib.transport.send_plan import single_window_plan
from ..lib.convert import to_bool, to_int, int_to_hex

def set_fun_mode(value=False):
    """Set the DIY Fun Mode (Drawing Mode)."""
    payload = bytes.fromhex("05000401") + bytes.fromhex("01" if to_bool(value) else "00")
    return single_window_plan("set_fun_mode", payload, requires_ack=True)

def set_pixel(x, y, color):
    """Set the color of a specific pixel."""
    x, y = map(to_int, [x, y])
    payload = bytes.fromhex("0a00050100") + bytes.fromhex(color) + bytes.fromhex(int_to_hex(x) + int_to_hex(y))
    return single_window_plan("set_pixel", payload, requires_ack=True)
