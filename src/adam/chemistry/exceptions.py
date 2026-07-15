"""Custom exception hierarchy for the chemistry package."""


class ChemistryError(Exception):
    """Base class for all chemistry-system errors."""


class InvalidQuantityError(ChemistryError):
    """Raised when a supplied quantity is invalid."""


class InsufficientQuantityError(ChemistryError):
    """Raised when less substance is available than an operation requires."""


class InvalidVolumeError(ChemistryError):
    """Raised when a compartment volume is invalid."""


class InvalidReactionError(ChemistryError):
    """Raised when a reaction definition is invalid."""


class InvalidNameError(ChemistryError):
    """Raised when a required name or symbol is invalid."""
