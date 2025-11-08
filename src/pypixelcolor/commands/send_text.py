# -*- coding: utf-8 -*-

"""

"""

# Imports
from logging import getLogger

# Locals
from ..lib.encode_text import encode_text
from ..lib.bit_tools import switch_endian, CRC32_checksum
from ..lib.convert import to_int, int_to_hex, validate_range

logger = getLogger("ipixel-cli.commands.send_text")

def send_text(text, rainbow_mode=0, animation=0, save_slot=1, speed=80, color="ffffff", font="default", font_offset_x=0, font_offset_y=0, font_size=0, matrix_height=16):
    """Send a text to the device with configurable parameters.

    Args:
        text (str): The text to send.
        rainbow_mode (int, optional): Rainbow mode (0-9). Defaults to 0.
        animation (int, optional): Animation type (0-7, except 3 and 4). Defaults to 0.
        save_slot (int, optional): Save slot (1-10). Defaults to 1.
        speed (int, optional): Animation speed (0-100). Defaults to 80.
        color (str, optional): Text color in hex. Defaults to "ffffff".
        font (str, optional): Font name. Defaults to "default".
        font_offset_x (int, optional): Font X offset. Defaults to 0.
        font_offset_y (int, optional): Font Y offset. Defaults to 0.
        font_size (int, optional): Font size. Defaults to 0 (auto).
        matrix_height (int, optional): Matrix height. Defaults to 16.

    Returns:
        bytes: Encoded command to send to the device.

    Raises:
        ValueError: If an invalid animation is selected or parameters are out of range.
    """
    
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

    # Magic numbers (pls, help me find out how they work)
    HEADER_1_MG = 0x1D
    HEADER_3_MG = 0xE
    # Dynamically calculate HEADER_GAP based on matrix_height (EXP)
    header_gap = 0x06 + matrix_height * 0x2

    header_1 = switch_endian(hex(HEADER_1_MG + len(text) * header_gap)[2:].zfill(4))
    header_2 = "000100"
    header_3 = switch_endian(hex(HEADER_3_MG + len(text) * header_gap)[2:].zfill(4))
    header_4 = "0000"
    header = header_1 + header_2 + header_3 + header_4
    
    save_slot_hex = hex(save_slot)[2:].zfill(4)       # Convert save slot to hex
    number_of_characters = int_to_hex(len(text))      # Number of characters
    
    properties = f"000101{int_to_hex(animation)}{int_to_hex(speed)}{int_to_hex(rainbow_mode)}ffffff00000000"
    characters = encode_text(text, matrix_height, color, font, (font_offset_x, font_offset_y), font_size)
    checksum = CRC32_checksum(number_of_characters + properties + characters)

    total = header + checksum + save_slot_hex + number_of_characters + properties + characters
    logger.debug(f"Full command data: \n{total}")

    return bytes.fromhex(total)
