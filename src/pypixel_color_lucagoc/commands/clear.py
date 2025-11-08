"""
Clear EEPROM command.
"""

def clear():
    """Clear the EEPROM."""
    return bytes.fromhex("04000380")