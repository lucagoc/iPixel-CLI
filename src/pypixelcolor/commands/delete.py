"""
Delete screen command.
"""

from ..lib.convert import to_int, int_to_hex

def delete_screen(n):
    """Delete a screen from the EEPROM."""
    return bytes.fromhex("070002010100") + bytes.fromhex(int_to_hex(to_int(n, "screen index")))
