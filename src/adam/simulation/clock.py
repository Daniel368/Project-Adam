from __future__ import annotations

import math

from adam.simulation.exceptions import InvalidTimeStepError


class SimulationClock:
    """Tracks elapsed simulation time and completed ticks."""

    def __init__(self) -> None:
        self._time = 0.0
        self._tick = 0

    @property
    def time(self) -> float:
        """Total elapsed simulation time."""
        return self._time

    @property
    def tick(self) -> int:
        """Number of successfully completed simulation steps."""
        return self._tick

    @staticmethod
    def validate_delta_time(delta_time: float) -> None:
        """Validate a proposed simulation time step."""
        if isinstance(delta_time, bool):
            raise InvalidTimeStepError("delta_time must not be a Boolean.")

        if not isinstance(delta_time, (int, float)):
            raise InvalidTimeStepError("delta_time must be a real number.")

        if not math.isfinite(delta_time):
            raise InvalidTimeStepError("delta_time must be finite.")

        if delta_time <= 0:
            raise InvalidTimeStepError("delta_time must be strictly positive.")

    def advance(self, delta_time: float) -> None:
        """Advance the clock by one valid time step."""
        self.validate_delta_time(delta_time)

        # Mutation happens only after validation, so failed advancement is atomic.
        self._time += float(delta_time)
        self._tick += 1
