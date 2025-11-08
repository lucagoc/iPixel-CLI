"""
Send image/animation commands to the device.
"""

from ..lib.bit_tools import CRC32_checksum, get_frame_size

def send_image(path_or_hex):
    """Send an image (PNG) or animation (GIF) to the device.
    
    Args:
        path_or_hex: Path to a .png or .gif file, or hexadecimal string
        
    Returns:
        bytes: Command to send to the device
    """
    # Determine if it's a file path or hex string
    is_gif = False
    if path_or_hex.endswith(".png"):
        with open(path_or_hex, "rb") as f:
            image_hex = f.read().hex()
        is_gif = False
    elif path_or_hex.endswith(".gif"):
        with open(path_or_hex, "rb") as f:
            image_hex = f.read().hex()
        is_gif = True
    else:
        # Assume hex string - try to detect format from content
        image_hex = path_or_hex
        # Check if it's a GIF by looking at the magic number (474946)
        is_gif = image_hex.startswith("474946")
    
    checksum = CRC32_checksum(image_hex)
    size = get_frame_size(image_hex, 8)
    
    if is_gif:
        # GIF animation command
        return bytes.fromhex(f"{get_frame_size('FFFF030000' + size + checksum + '0201' + image_hex, 4)}030000{size}{checksum}0201{image_hex}")
    else:
        # PNG image command
        return bytes.fromhex(f"{get_frame_size('FFFF020000' + size + checksum + '0065' + image_hex, 4)}020000{size}{checksum}0065{image_hex}")
