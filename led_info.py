#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import argparse
import logging
from bleak import BleakClient, BleakScanner

def setup_logging():
    log_format = '%(levelname)s %(message)s'
    
    formatter = logging.Formatter(log_format)
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    logging.basicConfig(level=logging.INFO, handlers=[handler])

logger = logging.getLogger(__name__)

async def scan_devices():
    dev_add=[]
    logger.info("Scanning for Bluetooth devices...")
    devices = await BleakScanner.discover(return_adv=True)#
    if devices:
        led_devices = [(device,advdata) for device,advdata in devices.values() if device.name and "LED" in device.name]
        logger.info(f"Found {len(led_devices)} device(s):")
        for device,adv in led_devices:
            adv_data = [f"{k:4X} => {v.hex(" ",1)}" for k,v in adv.manufacturer_data.items()]
            logger.info(f"  - {device.name} ({device.address}) {adv_data}")
            dev_add += [device.address]
        return dev_add
    else:
        logger.info("No Bluetooth devices found.")

def handle_rx(_, data):
        logger.info(f"  recv: {data.hex(" ",-2)}")

async def send_data(data, address, client):
        logger.info(f"  send: {data.hex(" ",-2)}")
        await client.write_gatt_char("0000fa02", data, response=True)
        await asyncio.sleep(0.5)
        
async def get_led_info(address):
    async with BleakClient(address) as client:
        logger.info(f"check: {address}")
        await client.start_notify("0000fa03", handle_rx)
        await send_data(bytes.fromhex("0800 0180 000000 00"), address, client) # set time
        await send_data(bytes.fromhex("0400 0580"), address, client) # get fw ver
        try:
            value = await client.read_gatt_descriptor(7) # "00002901-0000-1000-8000-00805f9b34fb"
            logger.info("  GATT_Descr(Handle 7) value: %r",  bytes(value))
        except:
            pass

if __name__ == "__main__":
    setup_logging()

    dev_add = asyncio.run(scan_devices())
    for address in dev_add:
        asyncio.run(get_led_info(address))
        
    input("Press Enter to exit...")

