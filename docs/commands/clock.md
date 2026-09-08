# Clock Mode

## `set_clock_mode`

::: pypixelcolor.commands.set_clock_mode.set_clock_mode
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
# Enable clock mode with default settings (style 1, 24-hour format, current date)
client.set_clock_mode()

# Set clock style 2 in 12-hour format without displaying date
client.set_clock_mode(style=2, format_24=False, show_date=False)

# Display a specific date (DD/MM/YYYY)
client.set_clock_mode(style=3, date="25/12/2026")
```

```bash
# Enable default clock mode
pypixelcolor -a <MAC_ADDRESS> -c set_clock_mode

# Set clock style 2 in 12-hour format
pypixelcolor -a <MAC_ADDRESS> -c set_clock_mode style=2 format_24=false show_date=false
```

## `set_time`

::: pypixelcolor.commands.set_time.set_time
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
# Synchronize device time with current local time
client.set_time()

# Set a specific time (e.g. 14:30:00)
client.set_time(hour=14, minute=30, second=0)
```

```bash
# Sync device time with current local time
pypixelcolor -a <MAC_ADDRESS> -c set_time

# Set a specific time
pypixelcolor -a <MAC_ADDRESS> -c set_time hour=14 minute=30 second=0
```
