from .img_2_pix import char_to_hex
from .bit_tools import switch_endian, invert_frames, logic_reverse_bits_order

def encode_text(text: str, matrix_height: int, color: str, font: str, font_offset: tuple[int, int], font_size: int) -> str:
    """Encode text to be displayed on the device.

    Args:
        text (str): The text to encode.
        matrix_height (int): The height of the LED matrix.
        color (str): The color in hex format (e.g., 'ffffff').
        font (str): The font name to use.
        font_offset (tuple[int, int]): The (x, y) offset for the font.
        font_size (int): The font size.

    Returns:
        str: The encoded text as a hexadecimal string.
    """
    result = ""
    matrix_height_hex = f"{matrix_height:02x}"
    
    for char in text:
        char_hex, char_width = char_to_hex(char, matrix_height, font=font, font_offset=font_offset, font_size=font_size)
        char_hex_converted = logic_reverse_bits_order(switch_endian(invert_frames(char_hex)))
        char_width_hex = f"{char_width:02x}"
        if char_hex:
            result += "80" + color +  char_width_hex + matrix_height_hex + char_hex_converted
            
    return result.lower()
