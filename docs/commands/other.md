# Other Commands

## `set_fun_mode`

::: pypixelcolor.commands.set_fun_mode.set_fun_mode
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
# Enable fun mode
client.set_fun_mode(True)

# Disable fun mode
client.set_fun_mode(False)
```

```bash
pypixelcolor -a <MAC_ADDRESS> -c set_fun_mode true
```

## `set_pixel`

::: pypixelcolor.commands.set_fun_mode.set_pixel
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
# Set pixel at coordinates (x=0, y=0) to red (#FF0000)
client.set_pixel(x=0, y=0, color="FF0000")

# Set pixel at coordinates (x=5, y=10) to green (#00FF00)
client.set_pixel(x=5, y=10, color="00FF00")
```

```bash
pypixelcolor -a <MAC_ADDRESS> -c set_pixel x=0 y=0 color=FF0000
```

## `set_rhythm_mode`

::: pypixelcolor.commands.set_rhythm_mode.set_rhythm_mode
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
# Set rhythm equalizer style 1 with custom level heights (0-15)
client.set_rhythm_mode(
    style=1,
    l1=4, l2=8, l3=12, l4=15, l5=10,
    l6=6, l7=3, l8=8, l9=12, l10=14, l11=5,
)
```

```bash
pypixelcolor -a <MAC_ADDRESS> -c set_rhythm_mode style=1 l1=4 l2=8 l3=12 l4=15 l5=10 l6=6 l7=3 l8=8 l9=12 l10=14 l11=5
```

## `set_rhythm_mode_2`

::: pypixelcolor.commands.set_rhythm_mode.set_rhythm_mode_2
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
# Set alternative rhythm mode (style 0 or 1, animation time 0-7)
client.set_rhythm_mode_2(style=1, t=3)
```

```bash
pypixelcolor -a <MAC_ADDRESS> -c set_rhythm_mode_2 style=1 t=3
```

## `set_timer`

Controls the timer (stopwatch) mode on the device.

::: pypixelcolor.commands.set_timer.set_timer
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
from pypixelcolor import TimerAction

# Using Enum
client.set_timer(TimerAction.START)
client.set_timer(TimerAction.PAUSE)
client.set_timer(TimerAction.STOP)

# Using string names
client.set_timer("start")
client.set_timer("pause")
client.set_timer("stop")
```

```bash
pypixelcolor -a <MAC_ADDRESS> -c set_timer start
```

## `set_scores`

Sets the scoreboard scores for player 1 and player 2 on supported devices.

::: pypixelcolor.commands.set_scores.set_scores
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
# Set Player 1 to 24 and Player 2 to 18
client.set_scores(score_p1=24, score_p2=18)
```

```bash
pypixelcolor -a <MAC_ADDRESS> -c set_scores score_p1=24 score_p2=18
```

