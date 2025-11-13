from enum import Enum
from typing import Any


class Font(Enum):
    """
    Enum Font for available fonts in the library.
    """

    CUSONG = "0_CUSONG16"
    FONSUG = "1_FONSUG16"
    VCR_OSD_MONO = "2_VCR_OSD_MONO"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value

    @classmethod
    def from_str(cls, val: Any) -> "Font":
        """Convert a string or Font to enum Font.

        Accepts either the enum member, the enum name (e.g. "FONSUG") or the
        raw value (e.g. "0_FONSUG"). Raises ValueError if unknown.
        """
        if isinstance(val, cls):
            return val
        if not isinstance(val, str):
            raise ValueError(f"Invalid font type: {type(val)!r}")
        # match by value or by name
        for member in cls:
            if member.value == val or member.name == val:
                return member
        raise ValueError(f"Unknown font: {val}")
