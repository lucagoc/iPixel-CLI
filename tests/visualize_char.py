#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick script to visualize a character rendering.

Usage:
    python tests/visualize_char.py A
    python tests/visualize_char.py A --size 24
    python tests/visualize_char.py "€" --size 16 --font 0_FONSUG
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pypixelcolor.commands.send_text import char_to_hex
from pypixelcolor.fonts.font_enum import Font


def hex_to_visual(hex_string: str, char_width: int, char_height: int) -> str:
    """
    Convert hex string to visual ASCII representation.
    
    Uses 2 characters per pixel to create square-like pixels in the terminal.
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


def main():
    parser = argparse.ArgumentParser(
        description="Visualize how a character is rendered",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests/visualize_char.py A
  python tests/visualize_char.py A --size 24
  python tests/visualize_char.py "€" --size 16 --font 0_FONSUG
  python tests/visualize_char.py "!" --size 16 --offset 0,2
        """
    )
    parser.add_argument('character', type=str, help='Character to visualize')
    parser.add_argument('--size', '-s', type=int, default=16,
                        help='Text size in pixels (default: 16)')
    parser.add_argument('--font', '-f', type=str, default=Font.VCR_OSD_MONO.value,
                        help=f'Font to use (default: {Font.VCR_OSD_MONO.value})')
    parser.add_argument('--offset', '-o', type=str, default='0,0',
                        help='Font offset as x,y (default: 0,0)')
    
    args = parser.parse_args()
    
    # Parse offset
    try:
        offset_x, offset_y = map(int, args.offset.split(','))
        font_offset = (offset_x, offset_y)
    except:
        print(f"❌ Invalid offset format: {args.offset}. Use format: x,y (e.g., 0,0)")
        sys.exit(1)
    
    # Generate the character
    try:
        hex_string, char_width = char_to_hex(
            character=args.character,
            text_size=args.size,
            font_offset=font_offset,
            font=args.font
        )
    except Exception as e:
        print(f"❌ Error generating character: {e}")
        sys.exit(1)
    
    # Display results
    print(f"\n{'='*60}")
    print(f"Character: '{args.character}'")
    print(f"Size: {args.size}px | Font: {args.font} | Offset: {font_offset}")
    print(f"{'='*60}\n")
    
    print(f"Width: {char_width} pixels")
    print(f"Hex string: {hex_string}\n")
    
    print("Visual representation:")
    visual = hex_to_visual(hex_string, char_width, args.size)
    print(visual)
    
    print(f"\n{'='*60}\n")
    
    # Pixel count
    pixel_count = bin(int(hex_string, 16))[2:].count('1') if hex_string else 0
    print(f"Total pixels: {pixel_count}")
    print(f"Hex length: {len(hex_string)} chars")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
