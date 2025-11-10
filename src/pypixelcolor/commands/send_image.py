import logging
import binascii
from pathlib import Path
from typing import Union, Optional
from PIL import Image
from PIL.Image import Palette
from io import BytesIO
from ..lib.transport.send_plan import SendPlan, Window, single_window_plan
from ..lib.device_info import DeviceInfo

logger = logging.getLogger(__name__)

# Helper functions for byte-level transformations
def _frame_size_bytes(length: int, size_hex_digits: int) -> bytes:
    """Return the length encoded as little-endian bytes.

    length: number of raw bytes
    size_hex_digits: number of hex digits used historically (e.g. 4 or 8). We convert to bytes = size_hex_digits//2
    """
    byte_count = size_hex_digits // 2
    return int(length).to_bytes(byte_count, byteorder="little")


def _crc32_le(data: bytes) -> bytes:
    """Return CRC32 as 4 bytes little-endian for the given raw bytes."""
    calculated_crc = binascii.crc32(data) & 0xFFFFFFFF
    return calculated_crc.to_bytes(4, byteorder="little")


def _len_prefix_for(inner: bytes) -> bytes:
    """Return 2-byte little-endian prefix matching legacy behavior for ('FFFF' + inner_hex).

    That legacy length was computed over 2 extra bytes (0xFF,0xFF) plus the inner payload.
    So prefix = (2 + len(inner)).to_bytes(2, 'little')
    """
    return int(2 + len(inner)).to_bytes(2, byteorder="little")

# Helper functions for image loading and resizing
def _load_from_file(path: Path) -> tuple[bytes, bool]:
    """Load image data from file path.
    
    Args:
        path: Path to image file (PNG or GIF).
        
    Returns:
        Tuple of (file_bytes, is_gif).
    """
    with open(path, "rb") as f:
        file_bytes = f.read()
    is_gif = path.suffix.lower() == ".gif"
    return file_bytes, is_gif


def _resize_and_crop_image(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """Resize and crop image to target dimensions while preserving aspect ratio.
    
    Args:
        img: PIL Image object.
        target_width: Target width in pixels.
        target_height: Target height in pixels.
        
    Returns:
        Resized and cropped PIL Image.
    """
    # Calculate aspect ratios
    img_aspect = img.width / img.height
    target_aspect = target_width / target_height
    
    if img_aspect > target_aspect:
        # Image is wider than target, fit by height and crop width
        new_height = target_height
        new_width = int(target_height * img_aspect)
    else:
        # Image is taller than target, fit by width and crop height
        new_width = target_width
        new_height = int(target_width / img_aspect)
    
    # Resize with aspect ratio preserved
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Calculate crop coordinates to center the image
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height
    
    # Crop to exact target size
    img_cropped = img_resized.crop((left, top, right, bottom))
    
    return img_cropped


def _resize_and_fit_image(img: Image.Image, target_width: int, target_height: int, background_color: tuple = (0, 0, 0)) -> Image.Image:
    """Resize and fit image to target dimensions while preserving aspect ratio (with padding).
    
    Args:
        img: PIL Image object.
        target_width: Target width in pixels.
        target_height: Target height in pixels.
        background_color: RGB tuple for padding color (default: black).
        
    Returns:
        Resized and fitted PIL Image with padding.
    """
    # Calculate aspect ratios
    img_aspect = img.width / img.height
    target_aspect = target_width / target_height
    
    if img_aspect > target_aspect:
        # Image is wider than target, fit by width
        new_width = target_width
        new_height = int(target_width / img_aspect)
    else:
        # Image is taller than target, fit by height
        new_height = target_height
        new_width = int(target_height * img_aspect)
    
    # Resize with aspect ratio preserved
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create new image with target size and background color
    # Use same mode as resized image to preserve palette/transparency
    if img_resized.mode in ('P', 'PA'):
        new_img = Image.new('P', (target_width, target_height))
        # Set palette from original image
        palette = img_resized.getpalette()
        if palette is not None:
            new_img.putpalette(palette)
    elif img_resized.mode in ('RGBA', 'LA'):
        new_img = Image.new('RGBA', (target_width, target_height), background_color + (255,))
    else:
        new_img = Image.new('RGB', (target_width, target_height), background_color)
    
    # Calculate paste coordinates to center the image
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2
    
    # Paste resized image onto background
    new_img.paste(img_resized, (paste_x, paste_y))
    
    return new_img


def _resize_image(file_bytes: bytes, is_gif: bool, target_width: int, target_height: int, fit_mode: str = 'crop') -> bytes:
    """Resize image to target dimensions while preserving aspect ratio (with center crop or fit).
    
    Args:
        file_bytes: Original image data.
        is_gif: Whether the image is a GIF.
        target_width: Target width in pixels.
        target_height: Target height in pixels.
        fit_mode: Resize mode - 'crop' (default) or 'fit'. 
                  'crop' will fill the entire target area and crop excess.
                  'fit' will fit the entire image with black padding.
        
    Returns:
        Resized image data as bytes.
    """
    img = Image.open(BytesIO(file_bytes))
    
    # Check if resize is needed
    needs_resize = img.size != (target_width, target_height)
    
    # Check if conversion from palette mode is needed
    needs_conversion = img.mode in ('P', 'PA', 'L', 'LA')
    
    if not needs_resize and not needs_conversion:
        logger.debug(f"Image already at target size {target_width}x{target_height} and in correct mode")
        return file_bytes
    
    if needs_resize:
        resize_method = "fit with padding" if fit_mode == 'fit' else "crop"
        logger.info(f"Resizing image from {img.size[0]}x{img.size[1]} to {target_width}x{target_height} (preserving aspect ratio with {resize_method})")
    
    if needs_conversion:
        logger.info(f"Converting image from mode {img.mode} to RGB (removing palette)")
    
    if is_gif:
        # Handle animated GIF
        frames = []
        durations = []
        disposal_methods = []
        
        try:
            frame_index = 0
            while True:
                # Resize frame with aspect ratio preserved (crop or fit based on mode)
                if needs_resize:
                    if fit_mode == 'fit':
                        processed_frame = _resize_and_fit_image(img, target_width, target_height)
                    else:
                        processed_frame = _resize_and_crop_image(img, target_width, target_height)
                else:
                    processed_frame = img
                
                # Keep frames in palette mode (P) for GIF compatibility
                # Only convert if necessary, preserving the original palette structure
                if processed_frame.mode in ('P', 'PA'):
                    # Already in palette mode, keep it
                    frames.append(processed_frame)
                elif processed_frame.mode in ('RGBA', 'LA'):
                    # Has transparency, convert to P with adaptive palette
                    frames.append(processed_frame.convert('P', palette=Palette.ADAPTIVE, colors=256))
                else:
                    # No transparency, convert to P with adaptive palette
                    frames.append(processed_frame.convert('P', palette=Palette.ADAPTIVE, colors=256))
                
                # Preserve animation metadata
                durations.append(img.info.get('duration', 100))
                disposal_methods.append(img.info.get('disposal', 2))  # 2 = restore to background
                
                frame_index += 1
                img.seek(frame_index)
        except EOFError:
            pass  # End of frames
        
        logger.info(f"Processing {len(frames)} frames for animated GIF")
        
        # Save resized GIF with preserved animation metadata
        output = BytesIO()
        frames[0].save(
            output,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=img.info.get('loop', 0),
            disposal=disposal_methods[0] if disposal_methods else 2,
            optimize=False  # Disable optimization to preserve exact frame data
        )
        
        # Size
        logger.info(f"Resized GIF to {len(output.getvalue())} bytes")
        
        # Debug: save resized GIF
        # debug_path = Path("tmp/resized_debug.gif")
        # debug_path.parent.mkdir(parents=True, exist_ok=True)
        # with open(debug_path, "wb") as f:
        #     f.write(output.getvalue())
        # logger.debug(f"Saved resized GIF to {debug_path}")
        
        return output.getvalue()
    else:
        # Handle static image (PNG)
        if needs_resize:
            if fit_mode == 'fit':
                resized_img = _resize_and_fit_image(img, target_width, target_height)
            else:
                resized_img = _resize_and_crop_image(img, target_width, target_height)
        else:
            resized_img = img
        # Convert to RGB to remove palette (P mode) and ensure compatibility
        resized_img = resized_img.convert('RGB')
        output = BytesIO()
        resized_img.save(output, format='PNG')
        
        # Debug: save resized PNG
        # debug_path = Path("tmp/resized_debug.png")
        # debug_path.parent.mkdir(parents=True, exist_ok=True)
        # with open(debug_path, "wb") as f:
        #     f.write(output.getvalue())
        # logger.debug(f"Saved resized PNG to {debug_path}")
        
        return output.getvalue()


def _load_from_hex(hex_string: str) -> tuple[bytes, bool]:
    """Load image data from hex string.
    
    Args:
        hex_string: Hexadecimal representation of image data.
        
    Returns:
        Tuple of (file_bytes, is_gif).
    """
    file_bytes = bytes.fromhex(hex_string)
    is_gif = hex_string.upper().startswith("474946")  # 'GIF' magic number
    return file_bytes, is_gif

# Main function to send image
def send_image(path_or_hex: Union[str, Path], fit_mode: str = 'crop', device_info: Optional[DeviceInfo] = None):
    """
    Send an image or animation.
    Supports PNG (static) and GIF (animated).
    
    Args:
        path_or_hex: Either a file path (str/Path) or hexadecimal string.
        device_info: Device information (injected automatically by DeviceSession).
        fit_mode: Resize mode - 'crop' (default) or 'fit'. 
                  'crop' will fill the entire target area and crop excess.
                  'fit' will fit the entire image with black padding.
        
    Returns:
        A SendPlan for sending the image/animation.
        
    Note:
        If device_info is available, the image will be automatically resized
        to match the target device dimensions if necessary.
    """
    # Robuste detection: try as Path first, fallback to hex
    try:
        path = Path(path_or_hex)
        if path.exists() and path.is_file():
            file_bytes, is_gif = _load_from_file(path)
        else:
            # Not a valid file path, treat as hex
            file_bytes, is_gif = _load_from_hex(str(path_or_hex))
    except (ValueError, OSError):
        # Path construction or file reading failed, treat as hex
        file_bytes, is_gif = _load_from_hex(str(path_or_hex))
    
    # Resize image if device_info is available and image is not hex string
    if device_info is not None and isinstance(path_or_hex, (str, Path)):
        try:
            path = Path(path_or_hex)
            if path.exists() and path.is_file():
                # Only resize actual image files, not hex strings
                file_bytes = _resize_image(file_bytes, is_gif, device_info.width, device_info.height, fit_mode)
        except (ValueError, OSError):
            # If it's a hex string, skip resizing
            pass

    # Prepare size and CRC in little-endian bytes
    size_bytes_4 = _frame_size_bytes(len(file_bytes), 8)  # 4 bytes little-endian
    checksum_bytes = _crc32_le(file_bytes)  # 4 bytes little-endian

    if not is_gif:
        # PNG: single window frame assembled in bytes
        inner = bytes([0x02, 0x00, 0x00]) + size_bytes_4 + checksum_bytes + bytes([0x00, 0x65]) + file_bytes
        prefix = _len_prefix_for(inner)
        data = prefix + inner
        return single_window_plan("send_image", data, requires_ack=True)

    # GIF: multi-window. Build per-window frames like legacy send_gif_windowed.
    size_bytes = size_bytes_4
    crc_bytes = checksum_bytes
    gif = file_bytes  # raw GIF data

    window_size = 12 * 1024
    windows = []
    pos = 0
    window_index = 0
    while pos < len(gif):
        window_end = min(pos + window_size, len(gif))
        chunk_payload = gif[pos:window_end]
        option = 0x00 if window_index == 0 else 0x02
        serial = 0x01 if window_index == 0 else 0x65
        cur_tail = bytes([0x02, serial])
        header = bytes([0x03, 0x00, option]) + size_bytes + crc_bytes + cur_tail
        frame = header + chunk_payload
        prefix = _len_prefix_for(frame)
        message = prefix + frame
        windows.append(Window(data=message, requires_ack=True))
        window_index += 1
        pos = window_end

    return SendPlan("send_image", windows)
