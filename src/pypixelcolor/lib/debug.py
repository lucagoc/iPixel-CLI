def print_character_from_hex(hex_string: str):
    """Print a character representation of a hexadecimal string."""
    # 9*16 pixels grid, 1 is for ON, 0 is for OFF
    # For each 4 hex characters, print a line in binary
    for i in range(0, len(hex_string), 4):
        line = bin(int(hex_string[i:i+4], 16))[2:].zfill(16)
        for j in range(0, 16, 1):
            if line[j] == "0":
                print("  ", end="")
            else:
                print("##", end="")
        print("")