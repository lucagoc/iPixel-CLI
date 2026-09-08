# Sending Content

## `send_image`

![Send Image](../assets/gifs/send_image.gif)

::: pypixelcolor.commands.send_image.send_image
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
from pypixelcolor import ResizeMethod

# Send a static image (PNG, JPG, BMP, etc.)
client.send_image("banner.png")

# Send an animated GIF with fit mode (preserves aspect ratio with black padding)
client.send_image("animation.gif", resize_method=ResizeMethod.FIT)

# Send an image and save it to slot 1
client.send_image("icon.png", save_slot=1)
```

```bash
# Send an image
pypixelcolor -a <MAC_ADDRESS> -c send_image banner.png

# Send an animated GIF with fit mode and save to slot 1
pypixelcolor -a <MAC_ADDRESS> -c send_image animation.gif resize_method=fit save_slot=1
```

## `send_image_hex`

::: pypixelcolor.commands.send_image.send_image_hex
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
from pypixelcolor import ResizeMethod

# Send an image from hex-encoded PNG data
hex_data = "89504e470d0a1a0a0000000d49484452..."
client.send_image_hex(hex_string=hex_data, file_extension=".png")

# Send animated GIF hex data with fit mode and save to slot 2
client.send_image_hex(
    hex_string="474946383961...",
    file_extension=".gif",
    resize_method=ResizeMethod.FIT,
    save_slot=2,
)
```

```bash
# Send image from hex data
pypixelcolor -a <MAC_ADDRESS> -c send_image_hex "<HEX_STRING>" .png
```

## `send_text`

<video controls width="100%" preload="metadata">
      <source src="../assets/videos/send_text.mp4" type="video/mp4">
      Your browser doesn't support videos.
    </video>

::: pypixelcolor.commands.send_text.send_text
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
from pypixelcolor import TextAnimation

# Simple static text
client.send_text("Hello World!")

# Scrolling text with custom color and animation speed
client.send_text(
    "Welcome to pypixelcolor!",
    animation=TextAnimation.SCROLL_LEFT,
    speed=90,
    color="00ff00",
)

# Text with background color, saved to slot 1
client.send_text("ALERT", color="ffffff", bg_color="ff0000", save_slot=1)
```

```bash
# Send static text
pypixelcolor -a <MAC_ADDRESS> -c send_text "Hello World!"

# Scrolling text with custom color and speed
pypixelcolor -a <MAC_ADDRESS> -c send_text "Welcome!" animation=scroll_left speed=90 color=00ff00
```

### Inline Color Tags

`send_text` supports inline hex color tags to style individual words or characters:

- Opening tag: `[#RRGGBB]` or `[RRGGBB]`
- Closing tag: `[/]`, `[/#]`, or `[/color]`

```python
# Multi-colored text
client.send_text("[#ff0000]Red[/] [#00ff00]Green[/] [#0000ff]Blue[/]")

# Nested tags (closes back to the parent color)
client.send_text("[#ffaa00]Orange [#ffffff]White[/] Orange[/]")
```

```bash
pypixelcolor -a <MAC_ADDRESS> -c send_text "[#ff0000]Red[/] [#00ff00]Green[/] [#0000ff]Blue[/]"
```

!!! note
    Inline color tags are supported with standard font rendering. When variable-width mode is enabled (`var_width=True`), color tags are ignored with a warning and the uniform `color` parameter is used instead.

### Animation Types

The `animation` parameter accepts a `TextAnimation` enum, a string name, or an integer:

| Value | Name | String | Description |
|---|---|---|---|
| `0` | `TextAnimation.STATIC` | `"static"` | Static text without animation (default) |
| `1` | `TextAnimation.SCROLL_LEFT` | `"scroll_left"` | Scrolls from right to left |
| `2` | `TextAnimation.SCROLL_RIGHT` | `"scroll_right"` | Scrolls from left to right |
| `3` | `TextAnimation.SCROLL_UP` | `"scroll_up"` | Scrolls upwards (32x32 devices only) |
| `4` | `TextAnimation.SCROLL_DOWN` | `"scroll_down"` | Scrolls downwards (32x32 devices only) |
| `5` | `TextAnimation.BLINK` | `"blink"` | Fast blinking text effect |
| `6` | `TextAnimation.FADE` | `"fade"` | Smooth blinking / breathing effect |
| `7` | `TextAnimation.SNOWFLAKE` | `"snowflake"` | Falling snowflake effect |

```python
from pypixelcolor import TextAnimation

# Using Enum
client.send_text("Hello", animation=TextAnimation.SCROLL_LEFT)

# Using string name
client.send_text("Alert!", animation="blink", speed=90)
```

### Font Configuration (`FontConfig`)

The `font` argument controls typography. It accepts a `FontConfig` instance (Python) or a configuration string (Python & CLI):

| Parameter | Type | Default | Description |
|---|---|---|---|
| `path` | `str` | Built-in UNIFONT | Path to a local `.ttf` or `.otf` file. |
| `font_size` | `int` | `char_height` | Font rendering size in pixels. |
| `offset` | `tuple[int, int]` | `(0, 0)` | Rendering offset `(x, y)`. |
| `pixel_threshold` | `int` | `128` | Binarization threshold (`0-255`). |
| `var_width` | `bool` | `False` | Enable variable-width rendering for proportional fonts. |

#### Usage Examples

```python
from pypixelcolor import FontConfig

# 1. Default font with variable-width
client.send_text("Hello", font=FontConfig(var_width=True))

# 2. Custom font from file
font = FontConfig.from_file("./fonts/retro.ttf", font_size=16, var_width=True)
client.send_text("Hello", font=font)

# 3. Inline key-value string
client.send_text("Hello", font="path=./fonts/retro.ttf,font_size=16,var_width=true")
```

```bash
# Default font with variable-width
pypixelcolor -a <MAC_ADDRESS> -c send_text "Hello" font=var_width=true

# Custom font file
pypixelcolor -a <MAC_ADDRESS> -c send_text "Hello" font=./retro.ttf

# Custom font with options
pypixelcolor -a <MAC_ADDRESS> -c send_text "Hello" font="path=./retro.ttf,font_size=16,var_width=true"
```

### Variable Width (`var_width`)

By default (`var_width=False`), each character is placed in a fixed-width slot (best for monospace fonts like UNIFONT). For proportional fonts, setting `var_width=True` renders text on a continuous canvas with natural kerning before slicing it into matrix chunks.

![Variable Width Rendering](../assets/pngs/var_width.png)

!!! warning "Limitations"
    - **Static text truncation**: With `animation=0` (`STATIC`), non-scrolling text exceeding screen width will be cut off. Use `scroll_left` for long text.
    - **Inline color tags**: Color tags (`[#ff0000]...[/]`) are not supported with `var_width=True` (they will be stripped with a warning and the uniform `color` used).




