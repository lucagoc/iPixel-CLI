from . import (
    clear,
    delete,
    get_device_info,
    set_brightness,
    set_clock_mode,
    set_rhythm_mode,
    set_fun_mode,
    set_time,
    set_orientation,
    set_power,
    send_text,
    send_image
)

COMMANDS = {
    "clear": clear.clear,
    "get_device_info": get_device_info.get_device_info,
    "set_brightness": set_brightness.set_brightness,
    "set_clock_mode": set_clock_mode.set_clock_mode,
    "set_rhythm_mode": set_rhythm_mode.set_rhythm_mode,
    "set_rhythm_mode_2": set_rhythm_mode.set_rhythm_mode_2,
    "set_time": set_time.set_time,
    "set_fun_mode": set_fun_mode.set_fun_mode,
    "set_pixel": set_fun_mode.set_pixel,
    "delete": delete.delete,
    "send_text": send_text.send_text,
    "set_orientation": set_orientation.set_orientation,
    "send_image": send_image.send_image,
    "set_power": set_power.set_power,
}