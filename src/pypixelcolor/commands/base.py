# -*- coding: utf-8 -*-

"""
Base types for command execution plans.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class AckPolicy:
    ack_per_window: bool = True
    ack_final: bool = True


@dataclass
class Window:
    data: bytes
    requires_ack: bool = True


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
