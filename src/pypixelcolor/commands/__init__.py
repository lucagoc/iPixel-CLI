from . import (
    clear,
    delete,
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
    "led_on": set_power.led_on,
    "led_off": set_power.led_off
}