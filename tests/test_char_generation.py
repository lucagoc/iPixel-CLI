# -*- coding: utf-8 -*-
"""Tests for character generation in send_text command."""

import pytest
import os
import json
from PIL import Image
from pathlib import Path

from pypixelcolor.commands.send_text import (
    char_to_hex,
    charimg_to_hex_string,
    get_font_path,
)
from pypixelcolor.fonts.font_enum import Font


# Directory for test fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "characters"
GOLDEN_DIR = FIXTURES_DIR / "golden"


def hex_to_visual(hex_string: str, char_width: int, char_height: int) -> str:
    """
    Convert hex string to visual ASCII representation for debugging.
    
    Uses 2 characters per pixel to create square-like pixels in the terminal.
    
    Args:
        hex_string: The hex string representation of the character
        char_width: Width of the character in pixels
        char_height: Height of the character in pixels
    
    Returns:
        ASCII art representation of the character
    """
    lines = []
    
    # Calculate hex chars per line based on width
    if char_width <= 8:
        hex_per_line = 2
        bits_to_read = 8
    elif char_width <= 16:
        hex_per_line = 4
        bits_to_read = 16
    elif char_width <= 24:
        hex_per_line = 6
        bits_to_read = 24
    else:
        hex_per_line = 8
        bits_to_read = 32
    
    for y in range(char_height):
        line_hex = hex_string[y * hex_per_line:(y + 1) * hex_per_line]
        if not line_hex:
            break
        line_value = int(line_hex, 16)
        
        # Convert to binary and create visual (2 chars per pixel for square aspect)
        binary_str = f"{line_value:0{bits_to_read}b}"[:char_width]
        visual_line = binary_str.replace('0', '··').replace('1', '██')
        lines.append(visual_line)
    
    return '\n'.join(lines)


def load_all_golden_test_cases():
    """
    Load all test cases from golden files in the fixtures directory.
    
    Returns:
        List of tuples (character, text_size, font) for parameterization
    """
    test_cases = []
    
    # Ensure directory exists
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find all JSON files in golden directory
    golden_files = list(GOLDEN_DIR.glob("*.json"))
    
    # Skip example/readme files
    golden_files = [f for f in golden_files if not f.name.startswith('.')]
    
    if not golden_files:
        raise FileNotFoundError("No golden files found in the fixtures directory.")
    
    # Load test cases from golden files
    for golden_file in golden_files:
        try:
            with open(golden_file, 'r') as f:
                data = json.load(f)
            
            text_size = data.get("text_size")
            font = data.get("font")
            characters = data.get("characters", {})
            
            # Add a test case for each character in this golden file
            for character in characters.keys():
                test_cases.append((character, text_size, font))
        except Exception as e:
            print(f"Warning: Could not load golden file {golden_file}: {e}")
            continue
    
    return test_cases if test_cases else [("A", 16, Font.VCR_OSD_MONO.value)]


class TestCharacterGeneration:
    """Test suite for character generation."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        # Ensure golden directory exists
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)

    @pytest.mark.parametrize("character,text_size,font", load_all_golden_test_cases())
    def test_char_to_hex_regression(self, character, text_size, font):
        """
        Test that character generation produces consistent output.
        
        This is a regression test using golden files grouped by size/font combination.
        Golden files contain multiple characters for the same configuration.
        On first run, it will generate/update the golden files.
        """
        # Generate the character
        hex_string, char_width = char_to_hex(
            character=character,
            text_size=text_size,
            font_offset=(0, 0),
            font=font
        )
        
        # Group by size and font (one file per combination)
        golden_file = GOLDEN_DIR / f"{text_size}_{font.replace('/', '_')}.json"
        
        # Load or create golden data
        if golden_file.exists():
            with open(golden_file, 'r') as f:
                golden_data = json.load(f)
        else:
            golden_data = {
                "text_size": text_size,
                "font": font,
                "characters": {}
            }
        
        # Check if this character exists in golden file
        if character in golden_data["characters"]:
            # Compare with expected values
            expected = golden_data["characters"][character]
            
            # Check hex string
            if hex_string != expected["hex_string"]:
                # Generate visual comparison for easier debugging
                expected_visual = hex_to_visual(expected["hex_string"], expected["char_width"], text_size)
                actual_visual = hex_to_visual(hex_string, char_width, text_size)
                
                error_msg = (
                    f"\n{'='*60}\n"
                    f"Hex string mismatch for '{character}' (size={text_size}, font={font})\n"
                    f"{'='*60}\n\n"
                    f"EXPECTED (width={expected['char_width']}):\n{expected_visual}\n\n"
                    f"GOT (width={char_width}):\n{actual_visual}\n\n"
                    f"Expected hex: {expected['hex_string']}\n"
                    f"Got hex:      {hex_string}\n"
                    f"{'='*60}\n"
                    f"\nTo visualize this character, run:\n"
                    f"  python -c \"from pypixelcolor.commands.send_text import char_to_hex; "
                    f"h, w = char_to_hex('{character}', {text_size}, (0, 0), '{font}'); print(h, w)\"\n"
                )
                assert False, error_msg
            
            assert char_width == expected["char_width"], (
                f"Character width mismatch for '{character}' (size={text_size}, font={font})\n"
                f"Expected: {expected['char_width']}\n"
                f"Got:      {char_width}"
            )
        else:
            # Add new character to golden file
            golden_data["characters"][character] = {
                "hex_string": hex_string,
                "char_width": char_width,
            }
            
            with open(golden_file, 'w') as f:
                json.dump(golden_data, f, indent=2, sort_keys=True)
            
            pytest.skip(f"Added '{character}' to golden file {golden_file.name}")

    @pytest.mark.parametrize("character,text_size,font_offset", [
        ("A", 16, (0, 0)),
        ("A", 16, (1, 0)),   # X offset
        ("A", 16, (0, 1)),   # Y offset
        ("A", 16, (-1, 0)),  # Negative X offset
        ("A", 16, (0, -1)),  # Negative Y offset
    ])
    def test_char_to_hex_with_offsets(self, character, text_size, font_offset):
        """Test that font offsets affect character generation."""
        hex_no_offset, width_no_offset = char_to_hex(
            character=character,
            text_size=text_size,
            font_offset=(0, 0),
            font=Font.VCR_OSD_MONO.value
        )
        
        hex_with_offset, width_with_offset = char_to_hex(
            character=character,
            text_size=text_size,
            font_offset=font_offset,
            font=Font.VCR_OSD_MONO.value
        )
        
        # Width should remain the same
        assert width_with_offset == width_no_offset
        
        # If offset is not (0, 0), hex should be different
        if font_offset != (0, 0):
            assert hex_with_offset != hex_no_offset, (
                f"Offset {font_offset} should change the rendered character"
            )

    def test_char_to_hex_returns_valid_hex(self):
        """Test that char_to_hex returns valid hexadecimal strings."""
        hex_string, char_width = char_to_hex(
            character="A",
            text_size=16,
            font_offset=(0, 0),
            font=Font.VCR_OSD_MONO.value
        )
        
        # Should be a valid hex string
        assert all(c in '0123456789ABCDEFabcdef' for c in hex_string)
        
        # Should not be empty
        assert len(hex_string) > 0
        
        # Width should be positive
        assert char_width > 0

    def test_char_to_hex_invalid_character(self):
        """Test handling of potentially problematic characters."""
        # Empty string should be handled gracefully
        # (might return None or empty hex depending on implementation)
        result = char_to_hex(
            character="",
            text_size=16,
            font_offset=(0, 0),
            font=Font.VCR_OSD_MONO.value
        )
        # Should not crash, result can be None or valid tuple
        assert result is not None

    @pytest.mark.parametrize("char_width,char_height", [
        (8, 16),
        (12, 16),
        (16, 16),
        (24, 16),
        (32, 16),
    ])
    def test_charimg_to_hex_string_different_widths(self, char_width, char_height):
        """Test charimg_to_hex_string with different character widths."""
        # Create a test image with a simple pattern
        img = Image.new('L', (char_width, char_height), 0)
        pixels = img.load()
        
        # Create a vertical line in the middle
        middle_x = char_width // 2
        for y in range(char_height):
            pixels[middle_x, y] = 255
        
        hex_string, returned_width = charimg_to_hex_string(img)
        
        # Should return valid hex
        assert all(c in '0123456789ABCDEFabcdef' for c in hex_string)
        
        # Should return correct width
        assert returned_width == char_width
        
        # Hex string length should match image dimensions
        # Each row is encoded based on width
        if char_width <= 8:
            expected_len = char_height * 2  # 2 hex chars per row
        elif char_width <= 16:
            expected_len = char_height * 4  # 4 hex chars per row
        elif char_width <= 24:
            expected_len = char_height * 6  # 6 hex chars per row
        else:
            expected_len = char_height * 8  # 8 hex chars per row
        
        assert len(hex_string) == expected_len

    def test_charimg_to_hex_string_pixel_perfect(self):
        """Test that pixel patterns are correctly encoded."""
        # Create a 16x16 test image with known pattern
        img = Image.new('L', (16, 16), 0)
        pixels = img.load()
        
        # Set first row to alternating pixels: 1010101010101010
        for x in range(0, 16, 2):
            pixels[x, 0] = 255
        
        hex_string, _ = charimg_to_hex_string(img)
        
        # First 4 hex chars should represent the alternating pattern
        first_row = hex_string[:4]
        # 1010101010101010 in binary = 0xAAAA in hex
        assert first_row.upper() == "AAAA"

    def test_all_common_characters(self):
        """Test generation of all common ASCII characters."""
        common_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:',.<>?/"
        
        for char in common_chars:
            hex_string, char_width = char_to_hex(
                character=char,
                text_size=16,
                font_offset=(0, 0),
                font=Font.VCR_OSD_MONO.value
            )
            
            # Each character should generate valid output
            assert hex_string is not None, f"Failed to generate hex for '{char}'"
            assert char_width > 0, f"Invalid width for '{char}'"
            assert all(c in '0123456789ABCDEFabcdef' for c in hex_string), (
                f"Invalid hex string for '{char}': {hex_string}"
            )

    def test_font_path_resolution(self):
        """Test that font paths are correctly resolved."""
        # Test existing fonts
        for font in Font:
            path = get_font_path(font.value)
            assert os.path.exists(path), f"Font path does not exist: {path}"
            assert path.endswith('.ttf'), f"Font should be a .ttf file: {path}"

    def test_character_consistency_across_runs(self):
        """Test that the same character generates identical output across multiple runs."""
        results = []
        
        for _ in range(5):
            hex_string, char_width = char_to_hex(
                character="X",
                text_size=16,
                font_offset=(0, 0),
                font=Font.VCR_OSD_MONO.value
            )
            results.append((hex_string, char_width))
        
        # All runs should produce identical results
        assert all(r == results[0] for r in results), (
            "Character generation is not deterministic"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
