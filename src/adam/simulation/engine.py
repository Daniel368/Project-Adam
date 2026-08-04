from __future__ import annotations

from collections.abc import Sequence

from adam.simulation.clock import SimulationClock
from adam.simulation.exceptions import (
    InvalidProcessError,
    InvalidStepCountError,
    ProcessRegistrationError,
)
from adam.simulation.process import SimulationProcess


class SimulationEngine:
    """Runs registered simulation processes in registration order.

    If a process fails during ``step``, processes that already ran are not
    rolled back. Later processes are skipped and the clock is not advanced.
    """

    def __init__(self) -> None:
        self._clock = SimulationClock()
        self._processes: list[SimulationProcess] = []

    @property
    def clock(self) -> SimulationClock:
        """The engine-owned simulation clock."""
        return self._clock

    @property
    def processes(self) -> Sequence[SimulationProcess]:
        """Registered processes as an immutable snapshot."""
        return tuple(self._processes)

    def add_process(self, process: SimulationProcess) -> None:
        """Register a process once, using identity for duplicate detection."""
        if not isinstance(process, SimulationProcess):
            raise InvalidProcessError(
                "process must provide a callable step(delta_time) operation."
            )

        if any(existing is process for existing in self._processes):
            raise ProcessRegistrationError(
                "The exact same process object is already registered."
            )

        self._processes.append(process)

    def remove_process(self, process: SimulationProcess) -> None:
        """Remove a registered process using identity."""
        for index, existing in enumerate(self._processes):
            if existing is process:
                del self._processes[index]
                return

        raise ProcessRegistrationError("The process is not registered.")

    def step(self, delta_time: float) -> None:
        """Run every process once, then advance the clock."""
        SimulationClock.validate_delta_time(delta_time)

        for process in self._processes:
            process.step(float(delta_time))

        self._clock.advance(float(delta_time))

    def run(self, steps: int, delta_time: float) -> None:
        """Call ``step`` exactly ``steps`` times."""
        if isinstance(steps, bool) or not isinstance(steps, int):
            raise InvalidStepCountError("steps must be an integer.")

        if steps < 0:
            raise InvalidStepCountError("steps must be non-negative.")

        # Validate even when steps == 0, keeping delta_time rules consistent.
        SimulationClock.validate_delta_time(delta_time)

        for _ in range(steps):
            self.step(float(delta_time))
