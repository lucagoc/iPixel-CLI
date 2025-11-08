"""
Delete screen command.
"""

from .base import single_window_plan
from ..lib.convert import to_int, int_to_hex

def delete_screen(n):
    """Delete a screen from the EEPROM."""
    payload = bytes.fromhex("070002010100") + bytes.fromhex(int_to_hex(to_int(n, "screen index")))
    return single_window_plan("delete_screen", payload, requires_ack=True)
