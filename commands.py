# -*- coding: utf-8 -*-

import datetime
from bit_tools import *
from img_2_pix import char_to_hex


# Utility functions
def to_bool(value):
    """Convert a value to a boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in {"true", "1", "yes"}:
        return True
    if isinstance(value, str) and value.lower() in {"false", "0", "no"}:
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def to_int(value, name="parameter"):
    """Convert a value to an integer."""
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Invalid integer value for {name}: {value}")


def int_to_hex(n):
    """Convert an integer to a 2-character hexadecimal string."""
    return f"{n:02x}"


def validate_range(value, min_val, max_val, name):
    """Validate that a value is within a specific range."""
    if not min_val <= value <= max_val:
        raise ValueError(f"{name} must be between {min_val} and {max_val}")


def encode_text(text: str, matrix_height: int, color: str, font: str, font_offset: tuple[int, int], font_size: int) -> str:
    """Encode text to be displayed on the device."""
    result = ""
    matrix_height_hex = f"{matrix_height:02x}"
    
    for char in text:
        char_hex, char_width = char_to_hex(char, matrix_height, font=font, font_offset=font_offset, font_size=font_size)
        char_hex_converted = logic_reverse_bits_order(switch_endian(invert_frames(char_hex)))
        char_width_hex = f"{char_width:02x}"
        if char_hex:
            result += "80" + color +  char_width_hex + matrix_height_hex + char_hex_converted
            print(result)
    return result.lower()

# Commands
def set_clock_mode(style=1, date="", show_date=True, format_24=True):
    """Set the clock mode of the device."""
    style = to_int(style, "style")
    show_date = to_bool(show_date)
    format_24 = to_bool(format_24)

    # Process date
    if not date:
        now = datetime.datetime.now()
        day, month, year = now.day, now.month, now.year % 100
        day_of_week = now.weekday() + 1
    else:
        try:
            day, month, year = map(int, date.split("/"))
            day_of_week = datetime.datetime(year, month, day).weekday() + 1
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

    return header + params + date_bytes


def set_rhythm_mode(style=0, l1 = "0", l2 = "0", l3 = "0", l4 = "0", l5 = "0", l6 = "0", l7 = "0", l8 = "0", l9 = "0", l10 = "0", l11 = "0"):
    """
    Set the rhythm mode of the device.
    :param style: The style of the rhythm mode (0-4).
    :param l1: Level 1 (0-15).
    :param l2: Level 2 (0-15).
    :param l3: Level 3 (0-15).
    :param l4: Level 4 (0-15).
    :param l5: Level 5 (0-15).
    :param l6: Level 6 (0-15).
    :param l7: Level 7 (0-15).
    :param l8: Level 8 (0-15).
    :param l9: Level 9 (0-15).
    :param l10: Level 10 (0-15).
    :param l11: Level 11 (0-15).
    :return: Byte sequence to set the rhythm mode.
    """
    
    header = bytes.fromhex("10000102")
    
    # Convert style to integer and validate range
    style = to_int(style, "style")
    validate_range(style, 0, 4, "rhythm mode style")

    # Convert levels to integers and validate ranges
    for l in [l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11]:
        l = to_int(l, "level")
        if not (0 <= l <= 15):
            raise ValueError(f"Level must be between 0 and 15, got {l}")
    
    # Convert levels to hexadecimal and concatenates
    data = "".join(
        int_to_hex(to_int(l)) for l in [l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11]
    )

    return header + bytes.fromhex(int_to_hex(style)) + bytes.fromhex(data)


def set_rhythm_mode_2(style=0, t=0):
    """
    Set the rhythm mode of the device (alternative version).
    :param style: The style of the rhythm mode (0-4).
    :param t: Animation time (0-7).
    :return: Byte sequence to set the rhythm mode.
    """
    
    header = bytes.fromhex("06000002")
    style = to_int(style, "style")
    validate_range(style, 0, 1, "rhythm mode style")
    t = to_int(t, "level")
    validate_range(t, 0, 7, "Level")
    
    return header + bytes([t]) + bytes.fromhex(int_to_hex(style))


def set_time(hour=None, minute=None, second=None):
    """Set the time of the device. If no time is provided, it uses the current system time."""
    if hour is None or minute is None or second is None:
        now = datetime.datetime.now()
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


def set_fun_mode(value=False):
    """Set the DIY Fun Mode (Drawing Mode)."""
    return bytes.fromhex("05000401") + bytes.fromhex("01" if to_bool(value) else "00")


def set_orientation(orientation=0):
    """Set the orientation of the device."""
    orientation = to_int(orientation, "orientation")
    validate_range(orientation, 0, 2, "Orientation")
    return bytes.fromhex("05000680") + bytes.fromhex(int_to_hex(orientation))


def clear():
    """Clear the EEPROM."""
    return bytes.fromhex("04000380")


def set_brightness(value):
    """Set the brightness of the device."""
    value = to_int(value, "brightness")
    validate_range(value, 0, 100, "Brightness")
    return bytes.fromhex("05000480") + bytes.fromhex(int_to_hex(value))


def set_speed(value):
    """Set the speed of the device. (Broken)"""
    value = to_int(value, "speed")
    validate_range(value, 0, 100, "Speed")
    return bytes.fromhex("050003") + bytes.fromhex(int_to_hex(value))


def set_pixel(x, y, color):
    """Set the color of a specific pixel."""
    x, y = map(to_int, [x, y])
    return bytes.fromhex("0a00050100") + bytes.fromhex(color) + bytes.fromhex(int_to_hex(x) + int_to_hex(y))


def led_off():
    """Turn the LED off."""
    return bytes.fromhex("0500070100")


def led_on():
    """Turn the LED on."""
    return bytes.fromhex("0500070101")


def send_text(text, rainbow_mode=0, animation=0, save_slot=1, speed=80, color="ffffff", font="default", font_offset_x=0, font_offset_y=0, font_size=0, matrix_height=16):
    """Send a text to the device with configurable parameters."""
    
    rainbow_mode = to_int(rainbow_mode, "rainbow mode")
    animation = to_int(animation, "animation")
    save_slot = to_int(save_slot, "save slot")
    speed = to_int(speed, "speed")
    font_offset_x = to_int(font_offset_x, "font offset x")
    font_offset_y = to_int(font_offset_y, "font offset y")
    font_size = to_int(font_size, "font size")
    matrix_height = to_int(matrix_height, "matrix height")
    
    for param, min_val, max_val, name in [
        (rainbow_mode, 0, 9, "Rainbow mode"),
        (animation, 0, 7, "Animation"),
        (save_slot, 1, 10, "Save slot"),
        (speed, 0, 100, "Speed"),
        (len(text), 1, 100, "Text length"),
        (matrix_height, 1, 128, "Matrix height")
    ]:
        validate_range(param, min_val, max_val, name)

    # Apply default font size if not specified
    if font_size == 0:
        font_size = matrix_height

    # Disable unsupported animations (bootloop)
    if animation == 3 or animation == 4:
        raise ValueError("Invalid animation for text display")

    header_1 = switch_endian(hex(0x1D + len(text) * 0x26)[2:].zfill(4))
    header_2 = "000100"
    header_3 = switch_endian(hex(0xE + len(text) * 0x26)[2:].zfill(4))
    header_4 = "0000"
    header = header_1 + header_2 + header_3 + header_4
    
    save_slot_hex = hex(save_slot)[2:].zfill(4)       # Convert save slot to hex
    number_of_characters = int_to_hex(len(text))      # Number of characters
    
    properties = f"000101{int_to_hex(animation)}{int_to_hex(speed)}{int_to_hex(rainbow_mode)}ffffff00000000"
    characters = encode_text(text, matrix_height, color, font, (font_offset_x, font_offset_y), font_size)
    checksum = CRC32_checksum(number_of_characters + properties + characters)

    return bytes.fromhex(header + checksum + save_slot_hex + number_of_characters + properties + characters)


def send_png(path_or_hex):
    """Send a PNG image to the device."""
    if path_or_hex.endswith(".png"):
        with open(path_or_hex, "rb") as f:
            png_hex = f.read().hex()
    else:
        png_hex = path_or_hex
    checksum = CRC32_checksum(png_hex)
    size = get_frame_size(png_hex, 8)
    return bytes.fromhex(f"{get_frame_size('FFFF020000' + size + checksum + '0065' + png_hex, 4)}020000{size}{checksum}0065{png_hex}")

def send_animation(path_or_hex):
    """Send a GIF animation to the device."""
    if path_or_hex.endswith(".gif"):
        with open(path_or_hex, "rb") as f:
            gif_hex = f.read().hex()
    else:
        gif_hex = path_or_hex

    checksum = CRC32_checksum(gif_hex)
    size = get_frame_size(gif_hex, 8)
    return bytes.fromhex(f"{get_frame_size('FFFF030000' + size + checksum + '0201' + gif_hex, 4)}030000{size}{checksum}0201{gif_hex}")


def delete_screen(n):
    """Delete a screen from the EEPROM."""
    return bytes.fromhex("070002010100") + bytes.fromhex(int_to_hex(to_int(n, "screen index")))
