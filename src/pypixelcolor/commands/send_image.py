"""
Send image/animation: return a SendPlan with single or multiple windows.

The command encapsulates all protocol-specific framing (headers/tails/length prefix),
so the transport stays generic.
"""

from pathlib import Path
from typing import Union
from ..lib.bit_tools import CRC32_checksum, get_frame_size
from ..lib.transport.send_plan import (
    SendPlan, Window, AckPolicy, single_window_plan
)


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


def send_image(path_or_hex: Union[str, Path]):
    """Return a SendPlan for an image (PNG) or animation (GIF).
    
    Args:
        path_or_hex: Either a file path (str/Path) or hexadecimal string.
        
    Returns:
        A SendPlan for sending the image/animation.
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

    return SendPlan(
        id="send_image",
        windows=windows,
        chunk_size=244,
        window_size=12 * 1024,
        ack_policy=AckPolicy(ack_per_window=True, ack_final=True),
    )
