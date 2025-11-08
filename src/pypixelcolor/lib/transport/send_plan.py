import asyncio
from dataclasses import dataclass, field
from typing import Iterable
from logging import getLogger

from .ack_manager import AckManager, AckPolicy
from .window import Window

logger = getLogger(__name__)

@dataclass
class SendPlan:
    id: str
    windows: Iterable[Window]
    chunk_size: int = 244
    window_size: int = 12 * 1024
    ack_policy: AckPolicy = field(default_factory=AckPolicy)


def single_window_plan(plan_id: str, data: bytes, *,
                       requires_ack: bool = True,
                       chunk_size: int = 244,
                       window_size: int = 12 * 1024,
                       ack_policy: AckPolicy | None = None) -> SendPlan:
    if ack_policy is None:
        ack_policy = AckPolicy()
    return SendPlan(
        id=plan_id,
        windows=[Window(data=data, requires_ack=requires_ack)],
        chunk_size=chunk_size,
        window_size=window_size,
        ack_policy=ack_policy,
    )

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
