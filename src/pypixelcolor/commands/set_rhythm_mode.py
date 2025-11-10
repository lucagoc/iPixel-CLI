from ..lib.transport.send_plan import single_window_plan
from ..lib.convert import to_int, validate_range, int_to_hex

def set_rhythm_mode(style=0, l1 = "0", l2 = "0", l3 = "0", l4 = "0", l5 = "0", l6 = "0", l7 = "0", l8 = "0", l9 = "0", l10 = "0", l11 = "0"):
    """
    Set the rhythm mode of the device.
    :param style: The style of the rhythm mode (0-4).
    :param l1: Level 1 (0-15).
    :param l2: Level 2 (0-15).
    :param l3: Level 3 (0-15).
    :param l4: Level 4 (0-15).
    :param l5: Level 5 (0-15).
    :param l6: Level 6 (0-15).
    :param l7: Level 7 (0-15).
    :param l8: Level 8 (0-15).
    :param l9: Level 9 (0-15).
    :param l10: Level 10 (0-15).
    :param l11: Level 11 (0-15).
    :return: Byte sequence to set the rhythm mode.
    """
    
    header = bytes.fromhex("10000102")
    
    # Convert style to integer and validate range
    style = to_int(style, "style")
    validate_range(style, 0, 4, "rhythm mode style")

    # Convert levels to integers and validate ranges
    for l in [l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11]:
        l = to_int(l, "level")
        if not (0 <= l <= 15):
            raise ValueError(f"Level must be between 0 and 15, got {l}")
    
    # Convert levels to hexadecimal and concatenates
    data = "".join(
        int_to_hex(to_int(l)) for l in [l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11]
    )

    payload = header + bytes.fromhex(int_to_hex(style)) + bytes.fromhex(data)
    return single_window_plan("set_rhythm_mode", payload, requires_ack=True)


def set_rhythm_mode_2(style=0, t=0):
    """
    Set the rhythm mode of the device (alternative version).
    :param style: The style of the rhythm mode (0-4).
    :param t: Animation time (0-7).
    :return: Byte sequence to set the rhythm mode.
    """
    
    header = bytes.fromhex("06000002")
    style = to_int(style, "style")
    validate_range(style, 0, 1, "rhythm mode style")
    t = to_int(t, "level")
    validate_range(t, 0, 7, "Level")
    
    payload = header + bytes([t]) + bytes.fromhex(int_to_hex(style))
    return single_window_plan("set_rhythm_mode_2", payload)
