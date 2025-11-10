# Imports
from datetime import datetime

# Locals
from ..lib.transport.send_plan import single_window_plan
from ..lib.convert import validate_range

# Commands
def set_clock_mode(style: int = 1, date="", show_date: bool = True, format_24: bool = True):
    """
    Set the clock mode of the device.

    Args:
        style (int, optional): The clock style (0-8). Defaults to 1.
        date (str, optional): The date to display (DD/MM/YYYY). Defaults to today.
        show_date (bool, optional): Whether to show the date. Defaults to True.
        format_24 (bool, optional): Whether to use 24-hour format. Defaults to True.

    Returns:
        bytes: Encoded command to send to the device.
    """
    if isinstance(show_date, str):
        show_date = show_date.lower() in ("true", "1", "yes", "on")
    if isinstance(format_24, str):
        format_24 = format_24.lower() in ("true", "1", "yes", "on")

    # Process date
    if not date:
        now = datetime.now()
        day, month, year = now.day, now.month, now.year % 100
        day_of_week = now.weekday() + 1
    else:
        try:
            day, month, year = map(int, date.split("/"))
            day_of_week = datetime(year, month, day).weekday() + 1
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid date format: {e}")

    # Validate ranges
    validate_range(style, 0, 8, "Clock mode")
    validate_range(day_of_week, 1, 7, "Day of week")
    validate_range(month, 1, 12, "Month")
    validate_range(day, 1, 31, "Day")
    validate_range(year, 0, 99, "Year")

    # Build byte sequence using direct bytes constructions
    header = bytes([
        11, # Command length 
        0,  # Reserved
        6,  # Command ID
        1   # Command type ID
    ])

    params = bytes([
        int(style) & 0xFF,                      # Clock style
        0x01 if bool(format_24) else 0x00,      # 24-hour format
        0x01 if bool(show_date) else 0x00,      # Show date
    ])

    date_bytes = bytes([
        year & 0xFF,                   # Year
        month & 0xFF,                  # Month
        day & 0xFF,                    # Day
        day_of_week & 0xFF,            # Day of week
    ])

    payload = header + params + date_bytes
    return single_window_plan("set_clock_mode", payload)
