# Imports
from datetime import datetime

# Locals
from ..lib.transport.send_plan import single_window_plan
from ..lib.convert import to_int, to_bool, validate_range, int_to_hex

# Commands
def set_clock_mode(style=1, date="", show_date=True, format_24=True):
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
    style = to_int(style, "style")
    show_date = to_bool(show_date)
    format_24 = to_bool(format_24)

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

    # Build byte sequence
    header = bytes.fromhex("0b000601")
    params = bytes.fromhex(int_to_hex(style) + ("01" if format_24 else "00") + ("01" if show_date else "00"))
    date_bytes = bytes.fromhex(int_to_hex(year) + int_to_hex(month) + int_to_hex(day) + int_to_hex(day_of_week))

    payload = header + params + date_bytes
    return single_window_plan("set_clock_mode", payload, requires_ack=False)
