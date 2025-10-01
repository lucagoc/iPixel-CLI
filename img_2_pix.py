# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import os

# Convert an image to a string of hexadecimal values
def image_to_rgb_string(image_path):
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

# Create an hex frame from a 9x16 character img
# For 16 lines, convert the first 9 pixels to a 2 bytes hex value
# bit shift the 9 bits to the left by 7.
# if the pixel is white, add 1 bit, else add 0
def charimg_to_hex_string(img):
    # Load the image
    img = img.convert("L")

    # Check if the image is 9x16 pixels
    if img.size != (9, 16):
        raise ValueError("The image must be 9x16 pixels")

    hex_string = ""

    for y in range(16):
        line_value = 0

        for x in range(9):
            pixel = img.getpixel((x, y))
            if pixel > 0:
                line_value |= (1 << (15 - x))  # Move the bit to the left by 7

        # Convert the value to a 4 bytes hex string
        hex_string += f"{line_value:04X}"

    return hex_string

# Do not forget to delete the cache folder if you change the font or its size !
def char_to_hex(character: str, offset=(0, 3), size=16, font_path="font/default") -> str:
    """
    Convert a character to its hexadecimal representation with an optional offset.
    """

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
                img_rgb = Image.new('RGB', (9, 16), (255, 255, 255))
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
            img = Image.new('1', (9, 16), 0)  # '1' : Disable antialiasing
            d = ImageDraw.Draw(img)
            d.text(offset, character, fill=1, font=ImageFont.truetype(font_path, size))

            img_rgb = img.convert('RGB')
            img_rgb.save(cache_file)

        return charimg_to_hex_string(img_rgb)
    except Exception as e:
        print(f"[ERROR] : {e}")
        return None