"""
Set power command.
"""
from .base import single_window_plan

def led_off():
    """Turn the LED off."""
    payload = bytes.fromhex("0500070100")
    return single_window_plan("led_off", payload, requires_ack=True)

def led_on():
    """Turn the LED on."""
    payload = bytes.fromhex("0500070101")
    return single_window_plan("led_on", payload, requires_ack=True)
