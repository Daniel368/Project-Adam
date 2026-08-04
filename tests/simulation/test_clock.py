import math

import pytest

from adam.simulation.clock import SimulationClock
from adam.simulation.exceptions import InvalidTimeStepError


def test_initial_time_is_zero() -> None:
    assert SimulationClock().time == 0.0


def test_initial_tick_is_zero() -> None:
    assert SimulationClock().tick == 0


def test_valid_advancement_updates_time() -> None:
    clock = SimulationClock()
    clock.advance(0.5)
    clock.advance(0.5)
    assert clock.time == pytest.approx(1.0)


def test_valid_advancement_increments_tick() -> None:
    clock = SimulationClock()
    clock.advance(0.5)
    clock.advance(0.5)
    assert clock.tick == 2


@pytest.mark.parametrize(
    "delta_time",
    [0.0, -1.0, math.nan, math.inf, -math.inf, True, False],
)
def test_invalid_time_step_fails(delta_time: float) -> None:
    with pytest.raises(InvalidTimeStepError):
        SimulationClock().advance(delta_time)


def test_failed_advancement_leaves_state_unchanged() -> None:
    clock = SimulationClock()
    clock.advance(0.5)

    with pytest.raises(InvalidTimeStepError):
        clock.advance(0.0)

    assert clock.time == pytest.approx(0.5)
    assert clock.tick == 1


def test_time_cannot_be_directly_assigned() -> None:
    clock = SimulationClock()
    with pytest.raises(AttributeError):
        clock.time = 10.0


def test_tick_cannot_be_directly_assigned() -> None:
    clock = SimulationClock()
    with pytest.raises(AttributeError):
        clock.tick = 10
