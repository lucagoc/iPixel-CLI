"""
Set power command.
"""

def led_off():
    """Turn the LED off."""
    return bytes.fromhex("0500070100")

def led_on():
    """Turn the LED on."""
    return bytes.fromhex("0500070101")
