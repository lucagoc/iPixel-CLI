# -*- coding: utf-8 -*-
"""Font resolution and device-specific utilities."""

from pathlib import Path
from typing import Union
from logging import getLogger

from ...lib.device_info import DeviceInfo
from ...lib.font_config import FontConfig, BUILTIN_FONTS

logger = getLogger(__name__)


def resolve_font_config(font: Union[str, Path, FontConfig]) -> FontConfig:
    """Resolve a font specification to a FontConfig object.

    Args:
        font: Either a built-in font name (str), a local file path (str/Path),
              or an existing FontConfig instance.

    Returns:
        FontConfig instance.

    Raises:
        ValueError: If font argument type is invalid.
        FileNotFoundError: If the font file or built-in font is not found.
    """
    if isinstance(font, FontConfig):
        return font

    if isinstance(font, Path):
        font_str = str(font)
    elif isinstance(font, str):
        font_str = font.strip()
    else:
        raise ValueError(f"Font must be a string, Path, or FontConfig, got {type(font)}")

    # 1. Check built-in fonts (case-insensitive)
    if font_str.upper() in BUILTIN_FONTS:
        return FontConfig.builtin(font_str.upper())

    # 2. Check local file path
    path = Path(font_str).expanduser()
    if path.is_file():
        return FontConfig.from_file(path)

    raise FileNotFoundError(
        f"Font '{font}' not found. Available built-in fonts: {list(BUILTIN_FONTS.keys())}"
    )


def get_char_height_from_device(device_info: DeviceInfo) -> int:
    """Map device dimensions to appropriate character height.

    Args:
        device_info (DeviceInfo): Device information with width and height.

    Returns:
        int: The recommended character height (16 or device height).
    """
    if device_info.height <= 20:
        return 16
    return device_info.height

