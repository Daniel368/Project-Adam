from __future__ import annotations

import pytest

from adam.simulation.engine import SimulationEngine
from adam.simulation.exceptions import (
    InvalidProcessError,
    InvalidStepCountError,
    ProcessRegistrationError,
)


class RecordingProcess:
    def __init__(self, name: str, log: list[str] | None = None) -> None:
        self.name = name
        self.calls: list[float] = []
        self.log = log

    def step(self, delta_time: float) -> None:
        self.calls.append(delta_time)
        if self.log is not None:
            self.log.append(self.name)


class EqualProcess(RecordingProcess):
    def __eq__(self, other: object) -> bool:
        return isinstance(other, EqualProcess)


class FailingProcess:
    def step(self, delta_time: float) -> None:
        raise RuntimeError("process failed")


class InvalidObject:
    pass


def test_valid_process_can_be_registered() -> None:
    engine = SimulationEngine()
    process = RecordingProcess("one")
    engine.add_process(process)
    assert engine.processes == (process,)


def test_invalid_process_is_rejected() -> None:
    with pytest.raises(InvalidProcessError):
        SimulationEngine().add_process(InvalidObject())


def test_same_object_cannot_be_registered_twice() -> None:
    engine = SimulationEngine()
    process = RecordingProcess("one")
    engine.add_process(process)

    with pytest.raises(ProcessRegistrationError):
        engine.add_process(process)


def test_equal_but_distinct_processes_can_both_be_registered() -> None:
    engine = SimulationEngine()
    first = EqualProcess("first")
    second = EqualProcess("second")
    engine.add_process(first)
    engine.add_process(second)
    assert len(engine.processes) == 2


def test_process_can_be_removed() -> None:
    engine = SimulationEngine()
    process = RecordingProcess("one")
    engine.add_process(process)
    engine.remove_process(process)
    assert engine.processes == ()


def test_removing_unregistered_process_fails() -> None:
    with pytest.raises(ProcessRegistrationError):
        SimulationEngine().remove_process(RecordingProcess("missing"))


def test_one_step_calls_every_process_once() -> None:
    engine = SimulationEngine()
    first = RecordingProcess("first")
    second = RecordingProcess("second")
    engine.add_process(first)
    engine.add_process(second)

    engine.step(0.25)

    assert first.calls == [0.25]
    assert second.calls == [0.25]


def test_processes_execute_in_registration_order() -> None:
    log: list[str] = []
    engine = SimulationEngine()
    engine.add_process(RecordingProcess("first", log))
    engine.add_process(RecordingProcess("second", log))

    engine.step(0.1)

    assert log == ["first", "second"]


def test_one_step_advances_clock_once() -> None:
    engine = SimulationEngine()
    engine.step(0.5)
    assert engine.clock.time == pytest.approx(0.5)
    assert engine.clock.tick == 1


def test_process_failure_prevents_clock_advancement() -> None:
    engine = SimulationEngine()
    engine.add_process(FailingProcess())

    with pytest.raises(RuntimeError, match="process failed"):
        engine.step(0.5)

    assert engine.clock.time == 0.0
    assert engine.clock.tick == 0


def test_process_failure_prevents_later_processes() -> None:
    later = RecordingProcess("later")
    engine = SimulationEngine()
    engine.add_process(FailingProcess())
    engine.add_process(later)

    with pytest.raises(RuntimeError):
        engine.step(0.5)

    assert later.calls == []


def test_run_executes_requested_number_of_steps() -> None:
    engine = SimulationEngine()
    process = RecordingProcess("one")
    engine.add_process(process)

    engine.run(steps=3, delta_time=0.2)

    assert process.calls == [0.2, 0.2, 0.2]
    assert engine.clock.tick == 3


def test_zero_steps_performs_no_work() -> None:
    engine = SimulationEngine()
    process = RecordingProcess("one")
    engine.add_process(process)

    engine.run(steps=0, delta_time=0.2)

    assert process.calls == []
    assert engine.clock.tick == 0


@pytest.mark.parametrize("steps", [-1, 1.5, "3", True, False])
def test_invalid_step_count_fails(steps: object) -> None:
    with pytest.raises(InvalidStepCountError):
        SimulationEngine().run(steps=steps, delta_time=0.1)


def test_returned_process_collection_cannot_mutate_engine_state() -> None:
    engine = SimulationEngine()
    process = RecordingProcess("one")
    engine.add_process(process)

    snapshot = engine.processes

    with pytest.raises(AttributeError):
        snapshot.append(RecordingProcess("two"))

    assert engine.processes == (process,)
