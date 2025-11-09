from ..lib.transport.send_plan import single_window_plan

def set_power(on: bool = True):
    """
    Set the power state of the device.
    Args:
        on: True to turn on, False to turn off.
    Returns:
        A SendPlan to set the power state.
    """
    if isinstance(on, str):
        on = on.lower() in ("true", "1", "yes", "on")
    
    # Build command
    cmd = bytes([
        5,      # Command header
        0,      # Reserved
        7,      # sub-command
        1,      # param
        1 if on else 0
    ])
    return single_window_plan("set_power", cmd)
