"""

"""

# Imports
from datetime import datetime

# Locals
from ..lib.convert import to_int, validate_range

def set_time(hour=None, minute=None, second=None):
    """
    Set the time of the device. If no time is provided, it uses the current system time.
    """
    if hour is None or minute is None or second is None:
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        second = now.second
    hour = to_int(hour, "hour")
    minute = to_int(minute, "minute")
    second = to_int(second, "second")
    
    validate_range(hour, 0, 23, "Hour")
    validate_range(minute, 0, 59, "Minute")
    validate_range(second, 0, 59, "Second")
    
    return bytes.fromhex("08000180") + bytes([hour, minute, second]) + bytes.fromhex("00")
