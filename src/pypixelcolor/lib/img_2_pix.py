# -*- coding: utf-8 -*-

from logging import getLogger
from PIL import Image, ImageDraw, ImageFont
import os

logger = getLogger(__name__)

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
    default_font = os.path.join(fonts_dir, "0_VCR_OSD_MONO")
    logger.warning(f"Font '{font_name}' not found. Using default font at {default_font}.")
    return default_font

def image_to_rgb_string(image_path: str) -> str | None:
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

def charimg_to_hex_string(img):
    """
    Convert a character image to a hexadecimal string.
    """

    # Load the image
    img = img.convert("L")
    char_width, char_height = img.size

    # Check if the image is char_width x char_height pixels
    if img.size != (char_width, char_height):
        raise ValueError("The image must be " + str(char_width) + "x" + str(char_height) + " pixels")

    hex_string = ""

    for y in range(char_height):
        line_value = 0
        line_value_2 = 0

        for x in range(char_width):
            pixel = img.getpixel((x, y))
            if pixel > 0:
                if x < 16:
                    line_value |= (1 << (15 - x))
                else:
                    line_value_2 |= (1 << (31 - x))

        # Merge line_value_2 into line_value for 32-bit value
        line_value = (line_value_2 << 16) | line_value

        # Convert the value to a 4 bytes hex string
        hex_string += f"{line_value:04X}"
        
        # Print the line value for debugging
        binary_str = f"{line_value:0{16}b}".replace('0', '.').replace('1', '#')
        logger.debug(binary_str)

    return hex_string, char_width

def char_to_hex(character: str, matrix_height:int, font_offset=(0, 0), font_size=16, font="default"):
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
        min_width = 9
        max_width = 16
        text_width = max(min_width, min(text_width, max_width))
        # print(f"[INFO] Character '{character}' width: {text_width}px")
        
        # Create final image with calculated width
        img = Image.new('1', (text_width, matrix_height), 0)
        d = ImageDraw.Draw(img)
        d.text(font_offset, character, fill=1, font=font_obj)

        img_rgb = img.convert('RGB')
        
        return charimg_to_hex_string(img_rgb)
    except Exception as e:
        logger.error(f"Error occurred while converting character to hex: {e}")
        return None, 0
