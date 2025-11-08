"""
Set power command.
"""
from ..lib.transport.send_plan import single_window_plan

def set_power(on: bool):
    """Set the LED power state.

    Args:
        on: True to turn on, False to turn off.
    """
    payload = bytes.fromhex(f"05000701{'01' if on else '00'}")
    return single_window_plan("set_power", payload, requires_ack=True)
