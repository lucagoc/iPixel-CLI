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

def charimg_to_hex_string(img: Image) -> str:
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
    logger.debug("="*char_width + " %i"%char_width)

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

def char_to_hex(character: str, matrix_height:int, font_offset=(0, 0), font_size=16, font="default", minmax_width=(9,16,1)) -> tuple[str, int]:
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
            min_width, max_width, step_width = minmax_width
            text_width = max(min_width, min(text_width, max_width))
            text_width = min([i if i>=text_width else max_width for i in range(min_width, max_width+1, step_width)])
            # print(f"[INFO] Character '{character}' width: {text_width}px")
            
            # Create final image with calculated width
            img = Image.new('1', (text_width, matrix_height), 0)
            d = ImageDraw.Draw(img)
            
            # center char (d.text(anchor=mm) req pillow 8.0+)
            H,W = matrix_height/2,text_width/2
            font_offset = (W+font_offset[0], H+font_offset[1])
            d.text(font_offset, character, fill=1, anchor="mm", font=font_obj)

            img_rgb = img.convert('RGB')
            img_rgb.save(cache_file)
            
            return charimg_to_hex_string(img_rgb)
    except Exception as e:
        logger.error(f"Error occurred while converting character to hex: {e}")
        return None, 0
        
