from ..lib.transport.send_plan import single_window_plan
from ..lib.convert import to_int, int_to_hex

def delete(n: int):
    """
    Delete a screen from the EEPROM.
    
    Args:
        n: The screen index to delete.
        
    Returns:
        A SendPlan for deleting the specified screen.
    """
    payload = bytes.fromhex("070002010100") + bytes.fromhex(int_to_hex(to_int(n, "screen index")))
    return single_window_plan("delete_screen", payload, requires_ack=True)
