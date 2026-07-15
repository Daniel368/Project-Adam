"""Define immutable molecule value objects."""

from dataclasses import dataclass

from src.adam.chemistry.exceptions import InvalidNameError


@dataclass(frozen=True)
class Molecule:
    """An immutable chemical molecule identifier.

    Parameters
    ----------
    name : str
        Human-readable molecule name.
    symbol : str
        Chemical symbol or formula.

    Attributes
    ----------
    name : str
        Human-readable molecule name.
    symbol : str
        Chemical symbol or formula.

    Raises
    ------
    InvalidNameError
        If either field is not a string or contains only whitespace.

    Notes
    -----
    Frozen dataclass instances are hashable and may therefore be used as
    dictionary keys or set elements.
    """

    name: str
    symbol: str

    def __post_init__(self) -> None:
        """Validate the molecule name and symbol after initialisation.

        Raises
        ------
        InvalidNameError
            If ``name`` or ``symbol`` is not a non-empty string.
        """
        if not isinstance(self.name, str):
            raise InvalidNameError("Molecule name must be a string.")

        if not isinstance(self.symbol, str):
            raise InvalidNameError("Molecule symbol must be a string.")

        if not self.name.strip():
            raise InvalidNameError(
                "Molecule name must not be empty or whitespace-only."
            )

        if not self.symbol.strip():
            raise InvalidNameError(
                "Molecule symbol must not be empty or whitespace-only."
            )
