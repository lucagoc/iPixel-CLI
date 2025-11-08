from lib.convert import to_bool, to_int, int_to_hex

def set_fun_mode(value=False):
    """Set the DIY Fun Mode (Drawing Mode)."""
    return bytes.fromhex("05000401") + bytes.fromhex("01" if to_bool(value) else "00")

def set_pixel(x, y, color):
    """Set the color of a specific pixel."""
    x, y = map(to_int, [x, y])
    return bytes.fromhex("0a00050100") + bytes.fromhex(color) + bytes.fromhex(int_to_hex(x) + int_to_hex(y))
