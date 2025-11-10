# -*- coding: utf-8 -*-

# Imports
from logging import getLogger
from typing import Optional
import binascii

# Locals
from ..lib.convert import validate_range
from ..lib.transport.send_plan import single_window_plan
from ..lib.device_info import DeviceInfo
from ..lib.img_2_pix import char_to_hex

logger = getLogger("ipixel-cli.commands.send_text")

# Helper functions for byte-level transformations
def _reverse_bits_16(n: int) -> int:
    """Reverse bits in a 16-bit integer."""
    n = ((n & 0xFF00) >> 8) | ((n & 0x00FF) << 8)
    n = ((n & 0xF0F0) >> 4) | ((n & 0x0F0F) << 4)
    n = ((n & 0xCCCC) >> 2) | ((n & 0x3333) << 2)
    n = ((n & 0xAAAA) >> 1) | ((n & 0x5555) << 1)
    return n

def _invert_frames_bytes(data: bytes) -> bytes:
    """Invert frames by 2-byte chunks (equivalent to previous invert_frames on hex string)."""
    if len(data) % 2 != 0:
        raise ValueError("Data length must be multiple of 2 bytes for frame inversion")
    chunks = [data[i:i+2] for i in range(0, len(data), 2)]
    chunks.reverse()
    return b"".join(chunks)

def _switch_endian_bytes(data: bytes) -> bytes:
    """Reverse the byte order of the data (equivalent to previous switch_endian on hex)."""
    return data[::-1]

def _logic_reverse_bits_order_bytes(data: bytes) -> bytes:
    """Reverse bit order in each 16-bit chunk."""
    if len(data) % 2 != 0:
        raise ValueError("Data length must be multiple of 2 bytes for bit reversal")
    out = bytearray()
    for i in range(0, len(data), 2):
        chunk = data[i:i+2]
        value = int.from_bytes(chunk, byteorder="big")
        rev = _reverse_bits_16(value)
        out += rev.to_bytes(2, byteorder="big")
    return bytes(out)

# Helper function to encode text
def _encode_text(text: str, matrix_height: int, color: str, font: str, font_offset: tuple[int, int], font_size: int) -> bytes:
    """Encode text to be displayed on the device.

    Returns raw bytes (not a hex string). Each character block is composed as:
      0x80 + color(3 bytes) + char_width(1 byte) + matrix_height(1 byte) + frame_bytes...

    Args:
        text (str): The text to encode.
        matrix_height (int): The height of the LED matrix.
        color (str): The color in hex format (e.g., 'ffffff').
        font (str): The font name to use.
        font_offset (tuple[int, int]): The (x, y) offset for the font.
        font_size (int): The font size.

    Returns:
        bytes: The encoded text as raw bytes ready to be appended to a payload.
    """
    result = bytearray()

    # Validate and convert color
    try:
        color_bytes = bytes.fromhex(color)
    except Exception:
        raise ValueError(f"Invalid color hex: {color}")
    if len(color_bytes) != 3:
        raise ValueError("Color must be 3 bytes (6 hex chars), e.g. 'ffffff'")

    matrix_height_byte = matrix_height & 0xFF

    for char in text:
        char_hex, char_width = char_to_hex(char, matrix_height, font=font, font_offset=font_offset, font_size=font_size)
        if not char_hex:
            continue

        # Convert hex string to raw bytes and apply byte-level transformations
        try:
            char_bytes = bytes.fromhex(char_hex)
        except Exception:
            # skip invalid char
            continue

        # invert frames (2-byte chunks), reverse endian (bytes), then reverse bits in each 16-bit chunk
        char_bytes = _invert_frames_bytes(char_bytes)
        char_bytes = _switch_endian_bytes(char_bytes)
        char_bytes = _logic_reverse_bits_order_bytes(char_bytes)

        # Build bytes for this character using bytes([...]) for small chunks to minimize overhead
        result += bytes([0x80])
        result += color_bytes
        result += bytes([char_width & 0xFF])
        result += bytes([matrix_height_byte])
        result += char_bytes

    return bytes(result)

# Main function to send text command
def send_text(text: str, 
              rainbow_mode: int = 0, 
              animation: int = 0, 
              save_slot: int = 1, 
              speed: int = 80, 
              color: str = "ffffff", 
              font: str = "0_VCR_OSD_MONO", 
              font_offset_x: int = 0, 
              font_offset_y: int = 0, 
              font_size: int = 0, 
              matrix_height: Optional[int] = None,
              device_info: Optional[DeviceInfo] = None
              ):
    """
    Send a text to the device with configurable parameters.

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
        matrix_height (int, optional): Matrix height. Auto-detected from device_info if not specified.
        device_info (DeviceInfo, optional): Device information (injected automatically by DeviceSession).

    Returns:
        bytes: Encoded command to send to the device.

    Raises:
        ValueError: If an invalid animation is selected or parameters are out of range.
    """
    
    # Auto-detect matrix_height from device_info if available
    if matrix_height is None:
        if device_info is not None:
            matrix_height = device_info.height
            logger.debug(f"Auto-detected matrix height from device: {matrix_height}")
        else:
            matrix_height = 16  # Default fallback
            logger.warning("Using default matrix height: 16")
    
    rainbow_mode = int(rainbow_mode)
    animation = int(animation)
    save_slot = int(save_slot)
    speed = int(speed)
    font_offset_x = int(font_offset_x)
    font_offset_y = int(font_offset_y)
    font_size = int(font_size)
    matrix_height = int(matrix_height)
    
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

    # Magic numbers (protocol specifics)
    HEADER_1_MG = 0x1D
    HEADER_3_MG = 0x0E
    # Dynamically calculate HEADER_GAP based on matrix_height
    header_gap = 0x06 + matrix_height * 0x2

    # Build payload as bytes instead of manipulating hex strings
    payload = bytearray()

    # header_1 and header_3 are 2-byte little-endian values (previously produced via switch_endian)
    header1_val = HEADER_1_MG + len(text) * header_gap
    payload += header1_val.to_bytes(2, byteorder="little")

    # header_2 was the static hex "000100" (3 bytes)
    payload += bytes.fromhex("000100")

    header3_val = HEADER_3_MG + len(text) * header_gap
    payload += header3_val.to_bytes(2, byteorder="little")

    # header_4 was two zero bytes
    payload += b"\x00\x00"

    # Prepare body parts
    # save_slot: previously hex(...).zfill(4) (2 bytes, big-endian in original concatenation)
    payload += save_slot.to_bytes(2, byteorder="big")

    # number_of_characters: single byte
    if len(text) > 0xFF:
        raise ValueError("Text too long: max 255 characters")
    num_chars_byte = len(text).to_bytes(1, byteorder="big")

    # properties: 3 fixed bytes + animation + speed + rainbow + 3 bytes color + 4 zero bytes
    try:
        color_bytes = bytes.fromhex(color)
    except Exception:
        raise ValueError(f"Invalid color hex: {color}")
    if len(color_bytes) != 3:
        raise ValueError("Color must be 3 bytes (6 hex chars), e.g. 'ffffff'")

    properties = bytearray()
    properties += bytes.fromhex("000101")
    properties += bytes([animation & 0xFF, speed & 0xFF, rainbow_mode & 0xFF])
    properties += color_bytes
    properties += b"\x00" * 4

    # characters: encode_text now returns bytes
    characters_bytes = _encode_text(text, matrix_height, color, font, (font_offset_x, font_offset_y), font_size)

    # CRC32 over (num_chars + properties + characters)
    data_for_crc = num_chars_byte + bytes(properties) + characters_bytes
    crc = binascii.crc32(data_for_crc) & 0xFFFFFFFF
    # original code used switch_endian on the hex CRC, so append as little-endian 4 bytes
    checksum_bytes = crc.to_bytes(4, byteorder="little")

    # Assemble final payload in the same order as original: header, checksum, save_slot, num_chars, properties, characters
    final_payload = bytearray()
    # header part already in payload (header1 + header2 + header3 + header4)
    final_payload += payload
    final_payload += checksum_bytes
    # save_slot already appended earlier in payload; to match original order, remove the earlier addition and append here instead
    # (We appended save_slot earlier for convenience; adjust by slicing)
    # original header length is 2 + 3 + 2 + 2 = 9 bytes
    header_len = 2 + 3 + 2 + 2
    header_part = bytes(payload[:header_len])
    # rebuild final_payload correctly
    final_payload = bytearray()
    final_payload += header_part
    final_payload += checksum_bytes
    final_payload += save_slot.to_bytes(2, byteorder="big")
    final_payload += num_chars_byte
    final_payload += properties
    final_payload += characters_bytes

    logger.debug(f"Full command payload (len={len(final_payload)}): {final_payload.hex()}")

    return single_window_plan("send_text", bytes(final_payload))
