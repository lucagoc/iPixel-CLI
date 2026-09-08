# Device Settings

## `set_power`

::: pypixelcolor.commands.set_power.set_power
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
# Turn on the display
client.set_power(True)

# Turn off the display
client.set_power(False)
```

```bash
# Turn on the display
pypixelcolor -a <MAC_ADDRESS> -c set_power true

# Turn off the display
pypixelcolor -a <MAC_ADDRESS> -c set_power false
```

## `set_brightness`

::: pypixelcolor.commands.set_brightness.set_brightness
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
# Set brightness to 50%
client.set_brightness(50)

# Set maximum brightness (100%)
client.set_brightness(100)
```

```bash
pypixelcolor -a <MAC_ADDRESS> -c set_brightness 50
```

## `set_orientation`

::: pypixelcolor.commands.set_orientation.set_orientation
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
# Set default orientation (0: 0°)
client.set_orientation(0)

# Rotate display (0: 0°, 1: 90°, 2: 180°, 3: 270°)
client.set_orientation(2)
```

```bash
pypixelcolor -a <MAC_ADDRESS> -c set_orientation 2
```

## `set_schedule`

::: pypixelcolor.commands.set_schedule.set_schedule
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
from pypixelcolor import ScheduleDay

# Turn ON at 08:00 every day (slot 0)
client.set_schedule(hour=8, minute=0, on=True, slot=0)

# Turn OFF at 23:00 on weekdays using ScheduleDay bitmask (slot 1)
client.set_schedule(
    hour=23,
    minute=0,
    on=False,
    days=ScheduleDay.MON | ScheduleDay.TUE | ScheduleDay.WED | ScheduleDay.THU | ScheduleDay.FRI,
    slot=1,
)

# Turn ON at 10:00 on weekends using string list (slot 2)
client.set_schedule(hour=10, minute=0, on=True, days=["sat", "sun"], slot=2)
```

```bash
# Turn ON at 08:00 every day
pypixelcolor -a <MAC_ADDRESS> -c set_schedule hour=8 minute=0 on=true slot=0

# Turn OFF at 23:00 on weekends
pypixelcolor -a <MAC_ADDRESS> -c set_schedule hour=23 minute=0 on=false days=sat,sun slot=1
```

::: pypixelcolor.commands.set_schedule.ScheduleDay
    options:
      show_root_heading: true
      show_root_toc_entry: false
