# -*- coding: utf-8 -*-
"""Font configuration and management."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os

UNIFONT_PATH = str(Path(__file__).resolve().parent.parent / "fonts" / "unifont.otf")

BUILTIN_FONTS: dict[str, str] = {
    "UNIFONT": UNIFONT_PATH,
}


@dataclass(frozen=True)
class FontConfig:
    """Configuration for a font.

    Attributes:
        name: Font identifier or display name.
        path: Path to the font file (.ttf / .otf).
        font_size: Optional font size override (defaults to char_height if None).
        offset: Rendering (x, y) offset tuple. Defaults to (0, 0).
        pixel_threshold: Binarization threshold (0-255). Defaults to 128.
        var_width: Whether variable width rendering mode is enabled. Defaults to False.
    """

    name: str
    path: str
    font_size: Optional[int] = None
    offset: tuple[int, int] = (0, 0)
    pixel_threshold: int = 128
    var_width: bool = False

    @classmethod
    def builtin(cls, name: str = "UNIFONT", **kwargs) -> "FontConfig":
        """Load a built-in font by name.

        Args:
            name: Name of the built-in font (e.g. UNIFONT).
            **kwargs: Optional configuration overrides (font_size, offset, pixel_threshold, var_width).

        Returns:
            FontConfig instance.

        Raises:
            ValueError: If font name is not recognized.
        """
        name_upper = name.upper()
        if name_upper not in BUILTIN_FONTS:
            raise ValueError(f"Unknown built-in font: {name}. Available: {list(BUILTIN_FONTS.keys())}")
        return cls(name=name_upper, path=BUILTIN_FONTS[name_upper], **kwargs)

    @classmethod
    def from_file(cls, path: str | Path, name: Optional[str] = None, **kwargs) -> "FontConfig":
        """Load a font from a local file path.

        Args:
            path: Path to .ttf or .otf file.
            name: Optional display name (defaults to filename stem).
            **kwargs: Optional configuration overrides (font_size, offset, pixel_threshold, var_width).

        Returns:
            FontConfig instance.

        Raises:
            FileNotFoundError: If the font file does not exist.
        """
        p = Path(path).expanduser().resolve()
        if not p.is_file():
            raise FileNotFoundError(f"Font file not found: {path}")
        return cls(name=name or p.stem, path=str(p), **kwargs)


def list_fonts() -> list[str]:
    """List all available built-in fonts.

    Returns:
        List of built-in font names.
    """
    return list(BUILTIN_FONTS.keys())

