# Managing Data

!!! Warning
    Using slots can cause bootloops if the send command contains corrupted data.
    Before sending data to a slot, make sure that sending works correctly without using slots.

The device provides "slots" to store the text and image data.
![Data slots](../assets/pngs/slots.png)

Saving content (text or image) in these slots is done via the `save_slot=` argument in their respective commands. This allows for faster access and reduces the time needed to display the content on the LED matrix.

## `clear`

::: pypixelcolor.commands.clear.clear
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
# Clear all device ROM data and settings
client.clear()
```

```bash
pypixelcolor -a <MAC_ADDRESS> -c clear
```

## `show_slot`

::: pypixelcolor.commands.show_slot.show_slot
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
# Display the content stored in slot 1
client.show_slot(1)
```

```bash
pypixelcolor -a <MAC_ADDRESS> -c show_slot 1
```

## `delete`

::: pypixelcolor.commands.delete.delete
    options:
      show_root_heading: false
      show_root_toc_entry: false

**Examples:**

```python
# Delete content stored in slot 1
client.delete(1)
```

```bash
pypixelcolor -a <MAC_ADDRESS> -c delete 1
```
