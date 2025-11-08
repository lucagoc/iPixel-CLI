"""
Set brightness command.
"""

from lib.convert import to_int, validate_range, int_to_hex

def set_brightness(value):
    """Set the brightness of the device."""
    value = to_int(value, "brightness")
    validate_range(value, 0, 100, "Brightness")
    return bytes.fromhex("05000480") + bytes.fromhex(int_to_hex(value))
