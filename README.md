# iPixel CLI

Python CLI rewrite of the "iPixel Color" application for LED Matrix displays manufactured by Taizhou Yumo Lighting Co., Ltd.
Tested only on a 96x16 display, but should work on other sizes (if not please open an issue).

⚠️ Still experimental, some commands might change in the future. ⚠️

## Features

- [x] 🔗 Connect to the device
- [x] 🔆 Set brightness
- [x] 🟥 Set pixels on screen
- [x] ⏲️ Set clock mode
- [x] 🎉 Set the display mode to fun mode (do not save display)
- [x] ✏️ Write text on the screen (with custom font support)
- [x] 💥 Clear memory
- [x] 🎢 Send animations
- [x] 🖼️ Write frames to EEPROM
- [x] ✅ Maintain connection to the device (WebSocket server)
- [x] 🔧 Change orientation
- [x] 🔧 Set the date
- [x] 🔧 Set the clock
- [x] 🔈 Rhythm mode
- [ ] 🔒 Set password

## Installation

Clone the repository and install the required packages.

```bash
git clone https://github.com/lucagoc/iPixel-CLI
cd iPixel-CLI
```

Then use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required packages.

```bash
pip install -r requirements.txt
```

## Usage

### ⚠️ WARNING ⚠️

Invalid data sent to the device can lead to BOOTLOOPS

While it is possible to recover from a bootloop by sending a clear command before the device tries to read the EEPROM, it is a little bit tricky and the timing is very short.
This tool is still experimental, use at your own risk.

Commands are executed using the following format:

### Getting started

Find the MAC address of your device using the `--scan` option:

```bash
python ipixelcli.py --scan
```

Then, use the `-a` option to specify the MAC address of your device, and the `-c` option to specify the command to execute:

```bash
python ipixelcli.py -a <DEVICE_MAC_ADDRESS> -c <COMMAND> [PARAMETERS]
```

`-c` can be used multiple times to send multiple commands in a single request.

Example:

```bash
python ipixelcli.py -a 4B:1E:2E:35:73:A3 -c set_brightness value=20 -c send_text "Hello World" rainbow_mode=9 speed=50 animation=1
```

---

## Commands

### `set_clock_mode`

**Description:** Set the clock mode of the device.

**Parameters:**

- `style` (int): Clock style (0-8). Default: 1
- `date` (str): Date in `DD/MM/YYYY` format. Default: current date
- `show_date` (bool): Show date (true/false). Default: true
- `format_24` (bool): 24-hour format (true/false). Default: true

---

### `set_rhythm_mode`

**Description:** Set the rhythm mode of the device (Frequency).

**Parameters:**

- `style` (int): Style (0-4). Default: 0
- `l1` to `l11` (int): Levels for each channel (0-15). Default: 0 for all channels

---

### `set_rhythm_mode_2`

**Description:** Set the rhythm mode of the device (Simple animation).

**Parameters:**

- `style` (int): Style (0-1). Default: 0
- `t` (int): Frame time of the animation (0-7). Default: 0

---

### `set_time`

**Description:** Set the time of the device.

**Parameters:**

- `hour` (int): Hour (0-23). Default: current hour
- `minute` (int): Minute (0-59). Default: current minute
- `second` (int): Second (0-59). Default: current second

If one or more parameter is missing, the current time will be used.

---

### `set_fun_mode`

**Description:** Set the DIY Fun Mode (Drawing Mode).

**Parameters:**

- `value` (bool): Enable or disable the mode (true/false). Default: false

---

### `set_orientation`

**Description:** Set the orientation of the device.

**Parameters:**

- `orientation` (int): Orientation value (0-3). Default: 0

---

### `clear`

**Description:** Clear the EEPROM.

**Parameters:**
None

---

### `set_brightness`

**Description:** Set the brightness of the device.

**Parameters:**

- `value` (int): Brightness level (0-100).

---

### `set_pixel`

**Description:** Set the color of a specific pixel. (EXPERIMENTAL)

**Parameters:**

- `x` (int): X-coordinate of the pixel.
- `y` (int): Y-coordinate of the pixel.
- `color` (str): Hexadecimal color value (e.g., `ff0000` for red).

---

### `send_text`

**Description:** Send a text to the device with configurable parameters.

**Parameters:**

- `text` (str): The text to display.
- `rainbow_mode` (int): Rainbow effect mode (0-9). Default: 0
- `animation` (int): Animation style (0-7). Default: 0
- `save_slot` (int): Save slot for the text (1-10). Default: 1
- `speed` (int): Speed of the text animation (0-100). Default: 80
- `color` (str): Hexadecimal color value. Default: `ffffff`
- `font` (str): Font name (without extension) located in the `fonts` folder. Default: `default`
- **`matrix_height`** (int): ⚠️ Height of the LED matrix (16, 20, 24). Default: 16
- `font_size` (int): font size (`.ttf` only)
- `font_offset_x` (int): Horizontal offset for the font (`.ttf` only). Default: 0
- `font_offset_y` (int): Vertical offset for the font (`.ttf` only). Default: 0

> ⚠️ The `matrix_height` parameter might be required for proper text rendering. If not specified, it defaults to 16. Please set it according to your LED matrix height (16, 20, 24, 32). Default font only provides proper rendering for 16 height matrices, use `font=VCR_OSD_MONO` for 24 height matrices.

> ⚠️ There is a known issue for matrix with 20px or 32px height, please try to change the value `HEADER_GAP` (line 245) in `commands.py` and report if it works.

---

### `send_png`

**Description:** Set the screen to display an image.

**Parameters:**

- `path_or_hex` (str): Path to the image PNG file or its hexadecimal representation.

---

### `send_animation`

**Description:** Send a GIF animation to the device, size must be 96x16 pixels and small.

**Parameters:**

- `path_or_hex` (str): Path to the GIF file or its hexadecimal representation.

---

### `delete_screen`

**Description:** Delete a screen from the EEPROM.

**Parameters:**

- `n` (int): Index of the screen to delete.

---

### `led_on`

**Description:** Turn the LED on.

**Parameters:** None

---

### `led_off`

**Description:** Turn the LED off.

**Parameters:** None

## WebSocket server

You can also start a basic WebSocket server using the following command :

```bash
python ipixelcli.py -a <bt_address> --server -p <port>
```

Then, send a request to the server with the following content:

```json
{
    "command": "<command>",
    "params": ["<param1>", "<param2>", "<param3>"]
}
```

For example :

```json
{
    "command": "send_text",
    "params": ["Hello World", "rainbow_mode=1", "speed=50"]
}
```

## Custom font

You can use a custom font by adding it to the fonts directory. This can be either:

- a `.ttf` font file, or
- a folder containing individual letter PNG files (see the `fonts/default` folder for reference). Files must be named using the Unicode code point of the character in hexadecimal (e.g., `0041.png` for 'A').

Then, specify the font name (without the file extension) with the `font` argument in the `send_text` command.
For `.ttf` files, adjust the font size and offset with `font_size`, `font_offset_x`, `font_offset_y` if necessary.
For best results, it is recommended to use a monospace font.

---
> ⚠️ The `fonts/cache` folder must be deleted if you change font offset or size.
---
> 💡 You can use the generated `fonts/cache` folder as a starting point for creating your own custom fonts from an existing font.

## Other

> 💡 If your terminal doesn't support emojis, you can disable them with the `--noemojis` flag.

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.
To get started on how to dump BLE logs from an Android device, refer to the [How to get BLE logs](docs/How_to_get_BLE_logs.md) guide.

Check also the [new repository iPixel-CFW](https://github.com/lucagoc/iPixel-CFW) to help us build a custom firmware for the iPixel device with more features !
