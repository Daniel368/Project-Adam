from typing import Protocol, runtime_checkable


@runtime_checkable
class SimulationProcess(Protocol):
    """An object that can advance by one simulation time step."""

    def step(self, delta_time: float) -> None:
        """Advance the process by elapsed simulation time."""
        ...
