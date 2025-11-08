"""
Send image/animation commands to the device.
"""

from ..lib.bit_tools import CRC32_checksum, get_frame_size

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
