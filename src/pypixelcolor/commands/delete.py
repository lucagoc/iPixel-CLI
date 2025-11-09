from ..lib.transport.send_plan import single_window_plan


def delete(n: int):
    """
    Delete a specific screen by its index.
    Args:
        n: Index of the screen to delete.
    Returns:
        A SendPlan to delete the specified screen.
    """
    if not (0 <= int(n) <= 255):
        raise ValueError("Screen index must be between 0 and 255")
    cmd = bytes([
        7,      # Command header
        0,      # Reserved
        2,      # sub-command
        1,      # param
        1,      # param
        0,      # param
        int(n)  # screen index
    ])
    return single_window_plan("delete_screen", cmd)
