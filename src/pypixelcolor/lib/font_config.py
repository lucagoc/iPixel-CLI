# -*- coding: utf-8 -*-
"""Font configuration and management."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

UNIFONT_PATH = str(Path(__file__).resolve().parent.parent / "fonts" / "unifont.otf")
BUILTIN_FONTS: dict[str, str] = {"UNIFONT": UNIFONT_PATH}


@dataclass(frozen=True)
class FontConfig:
    """Font rendering configuration."""

    path: str = UNIFONT_PATH
    name: str = "UNIFONT"
    font_size: Optional[int] = None
    offset: tuple[int, int] = (0, 0)
    pixel_threshold: int = 128
    var_width: bool = False

    @classmethod
    def default(cls, **kwargs) -> "FontConfig":
        return cls(**kwargs)

    @classmethod
    def builtin(cls, name: str = "UNIFONT", **kwargs) -> "FontConfig":
        return cls(name=name, **kwargs)

    @classmethod
    def from_file(cls, path: Union[str, Path], name: Optional[str] = None, **kwargs) -> "FontConfig":
        p = Path(path).expanduser().resolve()
        if not p.is_file():
            raise FileNotFoundError(f"Font file not found: {path}")
        return cls(path=str(p), name=name or p.stem, **kwargs)

    @classmethod
    def from_string(cls, font_str: str) -> "FontConfig":
        font_str = font_str.strip()
        if not font_str or font_str.upper() in ("UNIFONT", "DEFAULT"):
            return cls()
        if "=" not in font_str:
            return cls.from_file(font_str)

        kwargs = {}
        for item in font_str.split(","):
            if "=" in item:
                k, v = item.split("=", 1)
                k = k.strip().lower()
                v = v.strip()
                if v.lower() in ("true", "false"):
                    kwargs[k] = (v.lower() == "true")
                elif v.isdigit() or (v.startswith("-") and v[1:].isdigit()):
                    kwargs[k] = int(v)
                elif k == "offset":
                    parts = v.strip("()[] ").replace(";", ",").replace(":", ",").split(",")
                    kwargs[k] = (int(parts[0]), int(parts[1]))
                else:
                    kwargs[k] = v

        if "path" in kwargs:
            return cls.from_file(kwargs.pop("path"), **kwargs)
        return cls(**kwargs)


def list_fonts() -> list[str]:
    return list(BUILTIN_FONTS.keys())


