"""Store and manipulate molecule quantities."""

import math

from src.adam.chemistry.molecule import Molecule
from src.adam.chemistry.exceptions import (
    InvalidQuantityError,
    InsufficientQuantityError,
)

ZERO_TOLERANCE = 1e-12
"""float: Absolute tolerance used to normalise floating-point quantities."""


class ChemicalInventory:
    """A mutable mapping-like store of molecule quantities.

    Notes
    -----
    Missing molecules are treated as having quantity ``0.0``. The internal
    dictionary is never returned directly, so callers cannot mutate inventory
    state without using the public methods.

    Attributes
    ----------
    _quantities : dict[Molecule, float]
        Internal molecule-to-quantity mapping.
    """

    def __init__(self):
        """Create an empty chemical inventory."""
        self._quantities: dict[Molecule, float] = {}

    def get_quantity(self, molecule: Molecule) -> float:
        """Return the stored quantity of a molecule.

        Parameters
        ----------
        molecule : Molecule
            Molecule whose quantity is requested.

        Returns
        -------
        float
            Stored quantity, or ``0.0`` if the molecule is absent.
        """
        return self._quantities.get(molecule, 0.0)

    def add(self, molecule: Molecule, amount: float) -> None:
        """Increase the quantity of a molecule.

        Parameters
        ----------
        molecule : Molecule
            Molecule whose quantity will increase.
        amount : float
            Non-negative quantity to add.

        Raises
        ------
        InvalidQuantityError
            If ``amount`` is negative.
        """
        if amount < 0:
            raise InvalidQuantityError("Amount must not be negative.")

        current_amount = self.get_quantity(molecule)
        self._quantities[molecule] = current_amount + amount

    def remove(self, molecule: Molecule, amount: float) -> None:
        """Decrease the quantity of a molecule.

        Values sufficiently close to zero are normalised to exactly ``0.0``
        using :data:`ZERO_TOLERANCE`.

        Parameters
        ----------
        molecule : Molecule
            Molecule whose quantity will decrease.
        amount : float
            Non-negative quantity to remove.

        Raises
        ------
        InvalidQuantityError
            If ``amount`` is negative.
        InsufficientQuantityError
            If ``amount`` exceeds the available quantity beyond the floating-
            point tolerance.
        """
        if amount < 0:
            raise InvalidQuantityError("Amount cannot be negative.")

        current_quantity = self.get_quantity(molecule)

        if amount > current_quantity and not math.isclose(
            amount,
            current_quantity,
            abs_tol=ZERO_TOLERANCE,
        ):
            raise InsufficientQuantityError(
                "Inventory does not contain enough of this molecule."
            )

        new_quantity = current_quantity - amount

        if math.isclose(new_quantity, 0.0, abs_tol=ZERO_TOLERANCE):
            new_quantity = 0.0

        self._quantities[molecule] = new_quantity

    def contains(self, molecule: Molecule, amount: float) -> bool:
        """Check whether at least a requested quantity is available.

        Parameters
        ----------
        molecule : Molecule
            Molecule to inspect.
        amount : float
            Non-negative quantity required.

        Returns
        -------
        bool
            ``True`` when the stored quantity is at least ``amount``;
            otherwise ``False``.

        Raises
        ------
        InvalidQuantityError
            If ``amount`` is negative.
        """
        if amount < 0:
            raise InvalidQuantityError("Amount must not be negative.")

        return self.get_quantity(molecule) >= amount

    @property
    def as_mapping(self) -> dict[Molecule, float]:
        """Return a defensive copy of all stored quantities.

        Returns
        -------
        dict[Molecule, float]
            Independent molecule-to-quantity mapping.
        """
        return dict(self._quantities)
