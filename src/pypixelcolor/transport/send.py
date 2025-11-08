# -*- coding: utf-8 -*-
"""Generic sending utilities for SendPlan/Window.

No command-specific knowledge here. Just chunking, window ACKs, and final ACK.
"""
from __future__ import annotations

import asyncio
import logging

from ..commands.base import SendPlan

logger = logging.getLogger(__name__)


class AckManager:
    def __init__(self):
        self.window_event = asyncio.Event()
        self.all_event = asyncio.Event()

    def reset(self):
        self.window_event.clear()
        self.all_event.clear()

    def make_notify_handler(self):
        def handler(_, data: bytes):
            if not data:
                return
            try:
                logger.debug(f"Notify frame: {data.hex()}")
            except Exception:
                pass
            # Protocol: 0x05 ... code in data[4]
            if len(data) == 5 and data[0] == 0x05:
                if data[4] in (0, 1):
                    self.window_event.set()
                elif data[4] == 3:
                    self.window_event.set()
                    self.all_event.set()
                return
            b0 = data[0]
            b4 = data[4] if len(data) > 4 else None
            if b0 == 0x05 and b4 is not None:
                if b4 in (0, 1):
                    self.window_event.set()
                elif b4 == 3:
                    self.window_event.set()
                    self.all_event.set()
        return handler


def _chunk_bytes(buf: bytes, size: int):
    pos = 0
    total = len(buf)
    while pos < total:
        end = min(pos + size, total)
        yield buf[pos:end]
        pos = end


async def send_plan(client, plan: SendPlan, ack_mgr: AckManager, *, write_uuid: str = "0000fa02-0000-1000-8000-00805f9b34fb", ack_timeout: float = 8.0):
    """
    Send a SendPlan generically.

    - Iterate windows
    - Chunk by plan.chunk_size
    - Wait for ACK per window if required
    - Wait for final ACK if policy requires
    """
    logger.info(f"Sending plan '{plan.id}'")
    for idx, win in enumerate(plan.windows):
        ack_mgr.reset()
        # Send this window in chunks
        for chunk in _chunk_bytes(win.data, plan.chunk_size):
            await client.write_gatt_char(write_uuid, chunk, response=True)
        if plan.ack_policy.ack_per_window and win.requires_ack:
            try:
                await asyncio.wait_for(ack_mgr.window_event.wait(), timeout=ack_timeout)
            except asyncio.TimeoutError:
                raise RuntimeError("cur12k_no_answer: no ack from device")
    if plan.ack_policy.ack_final:
        try:
            await asyncio.wait_for(ack_mgr.all_event.wait(), timeout=ack_timeout)
        except asyncio.TimeoutError:
            # Some commands might not emit final ack; tolerate by default
            pass
