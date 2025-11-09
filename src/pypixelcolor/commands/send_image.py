"""
Send image/animation: return a SendPlan with single or multiple windows.

The command encapsulates all protocol-specific framing (headers/tails/length prefix),
so the transport stays generic.
"""

import logging
from pathlib import Path
from typing import Union, Optional
from PIL import Image
from PIL.Image import Palette
from io import BytesIO
from ..lib.bit_tools import CRC32_checksum, get_frame_size
from ..lib.transport.send_plan import SendPlan, Window, single_window_plan
from ..lib.device_info import DeviceInfo

logger = logging.getLogger(__name__)


def _hex_len_prefix_for(inner_hex: str) -> bytes:
    # Match legacy length prefix behavior
    return bytes.fromhex(get_frame_size("FFFF" + inner_hex, 4))


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


def _resize_image(file_bytes: bytes, is_gif: bool, target_width: int, target_height: int) -> bytes:
    """Resize image to target dimensions while preserving aspect ratio (with center crop).
    
    Args:
        file_bytes: Original image data.
        is_gif: Whether the image is a GIF.
        target_width: Target width in pixels.
        target_height: Target height in pixels.
        
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
        logger.info(f"Resizing image from {img.size[0]}x{img.size[1]} to {target_width}x{target_height} (preserving aspect ratio with center crop)")
    
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
                # Resize and crop frame with aspect ratio preserved
                processed_frame = _resize_and_crop_image(img, target_width, target_height) if needs_resize else img
                
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
        debug_path = Path("tmp/resized_debug.gif")
        debug_path.parent.mkdir(parents=True, exist_ok=True)
        with open(debug_path, "wb") as f:
            f.write(output.getvalue())
        logger.debug(f"Saved resized GIF to {debug_path}")
        
        return output.getvalue()
    else:
        # Handle static image (PNG)
        resized_img = _resize_and_crop_image(img, target_width, target_height) if needs_resize else img
        # Convert to RGB to remove palette (P mode) and ensure compatibility
        resized_img = resized_img.convert('RGB')
        output = BytesIO()
        resized_img.save(output, format='PNG')
        
        # Debug: save resized PNG
        debug_path = Path("tmp/resized_debug.png")
        debug_path.parent.mkdir(parents=True, exist_ok=True)
        with open(debug_path, "wb") as f:
            f.write(output.getvalue())
        logger.debug(f"Saved resized PNG to {debug_path}")
        
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


def send_image(path_or_hex: Union[str, Path], device_info: Optional[DeviceInfo] = None):
    """Return a SendPlan for an image (PNG) or animation (GIF).
    
    Args:
        path_or_hex: Either a file path (str/Path) or hexadecimal string.
        device_info: Device information (injected automatically by DeviceSession).
        
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
                file_bytes = _resize_image(file_bytes, is_gif, device_info.width, device_info.height)
        except (ValueError, OSError):
            # If it's a hex string, skip resizing
            pass

    image_hex = file_bytes.hex()
    checksum = CRC32_checksum(image_hex)  # endian-switched hex
    size_hex = get_frame_size(image_hex, 8)  # endian-switched hex len

    if not is_gif:
        # PNG: single window frame identical to legacy
        inner_hex = f"020000{size_hex}{checksum}0065{image_hex}"
        data = bytes.fromhex(get_frame_size("FFFF" + inner_hex, 4) + inner_hex)
        return single_window_plan("send_image", data, requires_ack=True)

    # GIF: multi-window. Build per-window frames like legacy send_gif_windowed.
    size_bytes = bytes.fromhex(size_hex)
    crc_bytes = bytes.fromhex(checksum)
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
        prefix = _hex_len_prefix_for(frame.hex())
        message = prefix + frame
        windows.append(Window(data=message, requires_ack=True))
        window_index += 1
        pos = window_end

    return SendPlan("send_image", windows)
