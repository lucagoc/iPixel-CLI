# -*- coding: utf-8 -*-

from logging import getLogger
from PIL import Image, ImageDraw, ImageFont
import os

logger = getLogger(__name__)

def get_font_path(font_name: str) -> str:
    """Get the path to the font directory or file."""
    # if file ttf exists
    if os.path.isfile("font/" + font_name + ".ttf"):
        return "font/" + font_name + ".ttf"
    # if folder exists
    elif os.path.isdir("font/" + font_name):
        return "font/" + font_name
    # else return default font
    else:
        logger.warning(f"Font '{font_name}' not found. Using default font.")
        return "font/default"

def image_to_rgb_string(image_path: str) -> str:
    """
    Convert an image to a hexadecimal RGB string.
    :param image_path: The path to the image file.
    """
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
        
        pixel_string = ""
        
        width, height = img.size
        
        for y in range(height):
            for x in range(width):
                r, g, b = img.getpixel((x, y))
                pixel_string += f"{r:02x}{g:02x}{b:02x}"
        
        return pixel_string
    except Exception as e:
        logger.error(f"Error occurred while converting image to RGB string: {e}")
        return None

def charimg_to_hex_string(img: Image) -> tuple[str, int]:
    """
    Convert a character image to a hexadecimal string.
    The width of each line is padded to the nearest multiple of `multiple` bits.
    :param img: The character image (PIL Image).
    Returns: (hex_string, width)
    """
    
    BYTE_SIZE = 8
    
    img = img.convert("L")
    char_width, char_height = img.size

    # Calculate padded width
    padded_width = ((char_width + BYTE_SIZE - 1) // BYTE_SIZE) * BYTE_SIZE

    hex_string = ""

    for y in range(char_height):
        line_value = 0

        for x in range(char_width):
            pixel = img.getpixel((x, y))
            if pixel > 0:
                line_value |= (1 << (padded_width - 1 - x))

        # Convert to hex, padding to nearest multiple of 4 digits
        hex_digits = ((padded_width + 3) // 4)
        hex_string += f"{line_value:0{hex_digits}X}"

        # Debug print
        binary_str = f"{line_value:0{padded_width}b}".replace('0', '.').replace('1', '#')
        logger.debug(binary_str)

    return hex_string, char_width

def char_to_hex(character: str, matrix_height:int, font_offset=(0, 0), font_size=16, font="default") -> tuple[str, int]:
    """
    Convert a character to its hexadecimal representation with an optional offset.
    Returns: (hex_string, width)
    """
    font_path = get_font_path(font)

    try:
        # Folder
        if os.path.isdir(font_path):
            if os.path.exists(font_path + "/" + str(matrix_height) + "p"):
                font_path = font_path + "/" + str(matrix_height) + "p"
                png_file = os.path.join(font_path, f"{ord(character):04X}.png")
                if os.path.exists(png_file):
                    img_rgb = Image.open(png_file)
                    return charimg_to_hex_string(img_rgb)
                else:
                    logger.warning(f"Cannot find PNG file : {png_file}, using a white image.")
                    # Create a white 9h image as fallback
                    img_rgb = Image.new('RGB', (9, matrix_height), (255, 255, 255))
                    return charimg_to_hex_string(img_rgb)
            else:
                logger.warning(f"Cannot find font data for font={font} and matrix_height={matrix_height}, using a white image.")
                # Create a white 9h image as fallback
                img_rgb = Image.new('RGB', (9, matrix_height), (255, 255, 255))
                return charimg_to_hex_string(img_rgb)
        
        # Else, check the font cache system
        font_name = os.path.splitext(os.path.basename(font_path))[0]
        
        # Create cache directory
        cache_dir = f"font/cache/{font_name}/{matrix_height}p{font_size}"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Cache file path
        cache_file = os.path.join(cache_dir, f"{ord(character):04X}.png")
        
        if os.path.exists(cache_file):
            # Use cached image
            img_rgb = Image.open(cache_file)
            return charimg_to_hex_string(img_rgb)
        else:
            # Generate image with dynamic width
            # First, create a temporary large image to measure text
            temp_img = Image.new('1', (100, matrix_height), 0)
            temp_draw = ImageDraw.Draw(temp_img)
            font_obj = ImageFont.truetype(font_path, font_size)
            
            # Get text bounding box
            bbox = temp_draw.textbbox((0, 0), character, font=font_obj)
            text_width = bbox[2] - bbox[0]
            
            # Clamp text_width between min and max values to prevent crash
            # Values tested on 16px height device
            # Might be different for 20px or 24px devices
            min_width = 9           # This is clearly due to byte alignment
            max_width = 16          # Probably same here
            text_width = max(min_width, min(text_width, max_width))
            # print(f"[INFO] Character '{character}' width: {text_width}px")
            
            # Create final image with calculated width
            img = Image.new('1', (text_width, matrix_height), 0)
            d = ImageDraw.Draw(img)
            d.text(font_offset, character, fill=1, font=font_obj)

            img_rgb = img.convert('RGB')
            img_rgb.save(cache_file)
            
            return charimg_to_hex_string(img_rgb)
    except Exception as e:
        logger.error(f"Error occurred while converting character to hex: {e}")
        return None, 0