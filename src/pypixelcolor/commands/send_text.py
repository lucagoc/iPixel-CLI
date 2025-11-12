# -*- coding: utf-8 -*-

# Imports
import os
import binascii
from PIL import Image, ImageDraw, ImageFont
from logging import getLogger
from typing import Optional, Union

# Locals
from ..fonts.font_enum import Font
from ..lib.transport.send_plan import single_window_plan
from ..lib.device_info import DeviceInfo
from ..fonts.font_enum import Font

logger = getLogger(__name__)

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

def get_font_path(font_name: str) -> str:
    """Get the path to the font directory or file."""
    # Get the base directory where fonts are stored (pypixelcolor/fonts)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fonts_dir = os.path.join(base_dir, "fonts")
    
    # Check if ttf file exists
    font_file = os.path.join(fonts_dir, f"{font_name}.ttf")
    if os.path.isfile(font_file):
        return font_file
    
    # Check if folder exists
    font_folder = os.path.join(fonts_dir, font_name)
    if os.path.isdir(font_folder):
        return font_folder
    
    # Return default font path
    default_font = os.path.join(fonts_dir, "0_VCR_OSD_MONO.ttf")
    logger.warning(f"Font '{font_name}' not found. Using default font at {default_font}.")
    return default_font


def charimg_to_hex_string(img: Image.Image) -> tuple[str, int]:
    """
    Convert a character image to a hexadecimal string.
    
    Args:
        img (PIL.Image): The character image.
    
    Returns:
        tuple: (hex_string, char_width)
    """

    # Load the image
    img = img.convert("L")
    char_width, char_height = img.size

    # Check if the image is char_width x char_height pixels
    if img.size != (char_width, char_height):
        raise ValueError("The image must be " + str(char_width) + "x" + str(char_height) + " pixels")

    hex_string = ""
    logger.debug("="*char_width + " %i"%char_width)

    for y in range(char_height):
        line_value = 0
        line_value_2 = 0

        for x in range(char_width):
            pixel = img.getpixel((x, y))
            if pixel > 0: # type: ignore
                if x < 16:
                    line_value |= (1 << (15 - x))
                else:
                    line_value_2 |= (1 << (31 - x))

        # Merge line_value_2 into line_value for 32-bit value
        line_value = (line_value_2) | (line_value << 16) if char_width > 16 else line_value

        # Convert the value to a hex string
        # Print the line value for debugging
        if char_width <= 8:
            line_value >>= 8
            hex_string +=  f"{line_value:02X}"
            binary_str = f"{line_value:0{8}b}".replace('0', '.').replace('1', '#')
        elif char_width <= 16:
            hex_string +=  f"{line_value:04X}"
            binary_str = f"{line_value:0{16}b}".replace('0', '.').replace('1', '#')
        elif char_width <= 24:
            line_value >>= 8
            hex_string +=  f"{line_value:06X}"
            binary_str = f"{line_value:0{24}b}".replace('0', '.').replace('1', '#')
        else:
            hex_string +=  f"{line_value:08X}"
            binary_str = f"{line_value:0{32}b}".replace('0', '.').replace('1', '#')            
        logger.debug(binary_str)

    return hex_string, char_width


def char_to_hex(character: str, text_size:int, font_offset: tuple[int, int], font: str):
    """
    Convert a character to its hexadecimal representation.
    
    Args:
        character (str): The character to convert.
        text_size (int): The size of the text (height of the matrix).
        font_offset (tuple[int, int]): The (x, y) offset for the font.
        font (str): The font name to use.
        
    Returns:
        tuple: (hex_string, char_width)
    """
    font_path = get_font_path(font)

    try:
        # Generate image with dynamic width
        # First, create a temporary large image to measure text
        temp_img = Image.new('1', (100, text_size), 0)
        temp_draw = ImageDraw.Draw(temp_img)
        font_obj = ImageFont.truetype(font_path, text_size)
        
        # Get text bounding box
        bbox = temp_draw.textbbox((0, 0), character, font=font_obj)
        text_width = bbox[2] - bbox[0]

        # Clamp text_width between min and max values to prevent crash
        # Values tested on 16px height device
        # Might be different for 20px or 24px devices
        min_width = 9
        max_width = 16
        text_width = int(max(min_width, min(text_width, max_width)))

        # Create final image with calculated width
        img = Image.new('1', (int(text_width), int(text_size)))
        d = ImageDraw.Draw(img)
        d.text(font_offset, character, fill=1, font=font_obj)

        img_rgb = img.convert('RGB')

        return charimg_to_hex_string(img_rgb)
    except Exception as e:
        logger.error(f"Error occurred while converting character to hex: {e}")
        return None, 0


def _encode_text(text: str, text_size: int, color: str, font: str, font_offset: tuple[int, int]) -> bytes:
    """Encode text to be displayed on the device.

    Returns raw bytes. Each character block is composed as:
      0x80 + color(3 bytes) + char_width(1 byte) + matrix_height(1 byte) + frame_bytes...

    Args:
        text (str): The text to encode.
        matrix_height (int): The height of the LED matrix.
        color (str): The color in hex format (e.g., 'ffffff').
        font (str): The font name to use.
        font_offset (tuple[int, int]): The (x, y) offset for the font.

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

    for char in text:
        char_hex, char_width = char_to_hex(char, text_size, font=font, font_offset=font_offset)
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
        result += bytes([text_size & 0xFF])
        result += char_bytes

    return bytes(result)


# Main function to send text command
def send_text(text: str,
              rainbow_mode: int = 0,
              animation: int = 0,
              save_slot: int = 1,
              speed: int = 80,
              color: str = "ffffff",
              font: Union[Font, str] = Font.FONGSUG,
              font_offset: tuple[int, int] = (0, 0),
              text_size: Optional[int] = None,
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
        text_size (int, optional): Text size. Auto-detected from device_info if not specified.
        device_info (DeviceInfo, optional): Device information (injected automatically by DeviceSession).

    Returns:
        bytes: Encoded command to send to the device.

    Raises:
        ValueError: If an invalid animation is selected or parameters are out of range.
    """
    
    # Auto-detect matrix_height from device_info if available
    if text_size is None:
        if device_info is not None:
            text_size = device_info.height
            logger.debug(f"Auto-detected matrix height from device: {text_size}")
        else:
            text_size = 16  # Default fallback
            logger.warning("Using default matrix height: 16")
    
    rainbow_mode = int(rainbow_mode)
    animation = int(animation)
    save_slot = int(save_slot)
    speed = int(speed)
    
    # Normalize font_offset to two integers (x, y)
    try:
        font_offset_x, font_offset_y = font_offset
        font_offset_x = int(font_offset_x)
        font_offset_y = int(font_offset_y)
    except Exception:
        raise ValueError("font_offset must be a tuple of two integers (x, y)")
    text_size = int(text_size)
    
    # Validate parameter ranges
    checks = [
        (rainbow_mode, 0, 9, "Rainbow mode"),
        (animation, 0, 7, "Animation"),
        (save_slot, 1, 10, "Save slot"),
        (speed, 0, 100, "Speed"),
        (len(text), 1, 100, "Text length"),
        (text_size, 1, 128, "Matrix height"),
    ]
    for param, min_val, max_val, name in checks:
        if not (min_val <= param <= max_val):
            raise ValueError(f"{name} must be between {min_val} and {max_val} (got {param})")

    # Normalize font: accept either FontName or str for backward compatibility
    if isinstance(font, Font):
        font_str = font.value
    else:
        font_str = str(font)

    # Disable unsupported animations (bootloop)
    if animation == 3 or animation == 4:
        raise ValueError("Invalid animation for text display")

    # Magic numbers (protocol specifics)
    HEADER_1_MG = 0x1D
    HEADER_3_MG = 0x0E
    # Dynamically calculate HEADER_GAP based on matrix_height
    header_gap = 0x06 + text_size * 0x2

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
    characters_bytes = _encode_text(text, text_size, color, font_str, (font_offset_x, font_offset_y))

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
