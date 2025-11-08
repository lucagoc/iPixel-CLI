"""
Clear EEPROM command.
"""

from .base import single_window_plan

def clear():
    """Clear the EEPROM."""
    payload = bytes.fromhex("04000380")
    return single_window_plan("clear", payload, requires_ack=True)
