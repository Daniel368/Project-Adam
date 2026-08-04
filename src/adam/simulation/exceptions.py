class SimulationError(Exception):
    """Base exception for simulation-domain errors."""


class InvalidTimeStepError(SimulationError):
    """Raised when a simulation time step is invalid."""


class InvalidProcessError(SimulationError):
    """Raised when an object does not satisfy SimulationProcess."""


class ProcessRegistrationError(SimulationError):
    """Raised when registering or removing a process fails."""


class InvalidStepCountError(SimulationError):
    """Raised when an engine run step count is invalid."""
