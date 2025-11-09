from ..lib.transport.send_plan import single_window_plan

def clear():
    """Clear the EEPROM."""
    cmd = bytes([
        4,     # Command header
        0,     # Reserved
        3,     # sub-command
        0x80,  # -128
    ])
    return single_window_plan("clear", cmd)
