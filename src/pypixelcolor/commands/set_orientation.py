from ..lib.transport.send_plan import single_window_plan

def set_orientation(orientation: int = 0):
    """
    Set the orientation of the device.
    
    Args:
        orientation (int): The orientation value to set (0-3).
    
    Returns:
        SendPlan: The command plan to set the orientation.
    """
    
    if (int(orientation) < 0 or int(orientation) > 3):
        raise ValueError("Orientation must be between 0 and 3")
    
    payload = bytes([
        5,
        0,
        6,
        0x80,
        int(orientation)
    ])
    return single_window_plan("set_orientation", payload)
