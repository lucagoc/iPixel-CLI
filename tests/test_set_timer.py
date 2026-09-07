# -*- coding: utf-8 -*-
"""Tests for set_timer command and TimerAction enum."""

import pytest
from pypixelcolor.models import TimerAction
from pypixelcolor.commands.set_timer import set_timer


def test_set_timer_enum():
    """Verify set_timer accepts TimerAction enum."""
    plan_start = set_timer(TimerAction.START)
    assert plan_start.id == "set_timer"
    windows = list(plan_start.windows)
    assert len(windows) == 1
    # 5th byte (index 4) is timer_action value: STOP = 0, START = 1, PAUSE = 2
    assert windows[0].data[4] == 1

    plan_stop = set_timer(TimerAction.STOP)
    assert list(plan_stop.windows)[0].data[4] == 0

    plan_pause = set_timer(TimerAction.PAUSE)
    assert list(plan_pause.windows)[0].data[4] == 2


def test_set_timer_strings():
    """Verify set_timer accepts string names."""
    # Standard names
    assert list(set_timer("start").windows)[0].data[4] == 1
    assert list(set_timer("stop").windows)[0].data[4] == 0
    assert list(set_timer("pause").windows)[0].data[4] == 2

    # Case insensitivity
    assert list(set_timer("START").windows)[0].data[4] == 1
    assert list(set_timer("Pause").windows)[0].data[4] == 2


def test_set_timer_integers():
    """Verify set_timer accepts direct integers."""
    assert list(set_timer(0).windows)[0].data[4] == 0
    assert list(set_timer(1).windows)[0].data[4] == 1
    assert list(set_timer(2).windows)[0].data[4] == 2
    assert list(set_timer("1").windows)[0].data[4] == 1


def test_set_timer_invalid_raises():
    """Verify invalid action raises ValueError."""
    with pytest.raises(ValueError, match="Invalid timer action"):
        set_timer("invalid_action")

    with pytest.raises(ValueError, match="Invalid timer action"):
        set_timer(99)
