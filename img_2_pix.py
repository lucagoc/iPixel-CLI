# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import os

CARACTER_WIDTH = 9
CARACTER_HEIGHT = 16

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
        print(f"[WARNING] Font '{font_name}' not found. Using default font.")
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
        print(f"[ERROR] : {e}")
        return None

def charimg_to_hex_string(img: Image) -> str:
    """
    Convert a character image to a hexadecimal string.
    """

    # Load the image
    img = img.convert("L")

    # Check if the image is CARACTER_WIDTH x CARACTER_HEIGHT pixels
    if img.size != (CARACTER_WIDTH, CARACTER_HEIGHT):
        raise ValueError("The image must be " + str(CARACTER_WIDTH) + "x" + str(CARACTER_HEIGHT) + " pixels")

    hex_string = ""

    for y in range(CARACTER_HEIGHT):
        line_value = 0

        for x in range(CARACTER_WIDTH):
            pixel = img.getpixel((x, y))
            if pixel > 0:
                line_value |= (1 << (CARACTER_HEIGHT - 1 - x))  # Move the bit to the left by 7

        # Convert the value to a 4 bytes hex string
        hex_string += f"{line_value:04X}"

    return hex_string

# Do not forget to delete the cache folder if you change the font or its size !
def char_to_hex(character: str, offset=(0, 0), size=CARACTER_HEIGHT, font="default") -> str:
    """
    Convert a character to its hexadecimal representation with an optional offset.
    """
    font_path = get_font_path(font)

    try:
        # Folder
        if os.path.isdir(font_path):
            png_file = os.path.join(font_path, f"{ord(character):04X}.png")
            if os.path.exists(png_file):
                img_rgb = Image.open(png_file)
                return charimg_to_hex_string(img_rgb)
            else:
                print(f"[WARNING] Cannot find PNG file : {png_file}, using a white image.")
                # Create a white 9x16 image
                img_rgb = Image.new('RGB', (CARACTER_WIDTH, CARACTER_HEIGHT), (255, 255, 255))
                return charimg_to_hex_string(img_rgb)
        
        # Else, check the font cache system
        font_name = os.path.splitext(os.path.basename(font_path))[0]
        
        # Create cache directory
        cache_dir = f"font/cache/{font_name}"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Cache file path
        cache_file = os.path.join(cache_dir, f"{ord(character):04X}.png")
        
        if os.path.exists(cache_file):
            # Use cached image
            img_rgb = Image.open(cache_file)
        else:
            # Generate image
            img = Image.new('1', (CARACTER_WIDTH, CARACTER_HEIGHT), 0)  # '1' : Disable antialiasing
            d = ImageDraw.Draw(img)
            d.text(offset, character, fill=1, font=ImageFont.truetype(font_path, size))

            img_rgb = img.convert('RGB')
            img_rgb.save(cache_file)

        return charimg_to_hex_string(img_rgb)
    except Exception as e:
        print(f"[ERROR] : {e}")
        return None