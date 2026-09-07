# Sending Content

## `send_image`

![Send Image](../assets/gifs/send_image.gif)

::: pypixelcolor.commands.send_image.send_image
    options:
      show_root_heading: false
      show_root_toc_entry: false

## `send_image_hex`

::: pypixelcolor.commands.send_image.send_image_hex
    options:
      show_root_heading: false
      show_root_toc_entry: false

## `send_text`

![Send Text](../assets/gifs/send_text.gif)

::: pypixelcolor.commands.send_text.send_text
    options:
      show_root_heading: false
      show_root_toc_entry: false

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

### Font Selection

The `font` argument supports multiple formats:

- **Built-in Font**: `"UNIFONT"` (default GNU Unifont with comprehensive Unicode and CJK glyph support).
- **Local Font Path**: Provide a relative or absolute path to a `.ttf` or `.otf` file (e.g. `font="./Minecraft.ttf"`).
- **FontConfig**: Pass a `FontConfig` object (e.g. `FontConfig.from_file("./Minecraft.ttf", font_size=16)`).
