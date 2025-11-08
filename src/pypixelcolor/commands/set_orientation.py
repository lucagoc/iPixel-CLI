from .base import single_window_plan
from ..lib.convert import to_int, validate_range, int_to_hex

def set_orientation(orientation=0):
    """Set the orientation of the device."""
    
    orientation = to_int(orientation, "orientation")
    validate_range(orientation, 0, 3, "Orientation")
    
    payload = bytes.fromhex("05000680") + bytes.fromhex(int_to_hex(orientation))
    return single_window_plan("set_orientation", payload, requires_ack=True)
