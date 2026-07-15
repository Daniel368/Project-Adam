"""Model chemical compartments and transfers between them."""

from __future__ import annotations

from src.adam.chemistry.inventory import ChemicalInventory
from src.adam.chemistry.molecule import Molecule
from src.adam.chemistry.exceptions import (
    ChemistryError,
    InvalidNameError,
    InvalidVolumeError,
    InvalidQuantityError,
    InsufficientQuantityError,
)


class Compartment:
    """A fixed-volume container that stores quantities of molecules.

    Parameters
    ----------
    name : str
        Human-readable name of the compartment. It must contain at least one
        non-whitespace character.
    volume : float
        Positive volume of the compartment.

    Attributes
    ----------
    name : str
        Human-readable compartment name.
    volume : float
        Fixed compartment volume.
    inventory : ChemicalInventory
        Inventory containing the molecules currently in the compartment.

    Raises
    ------
    InvalidNameError
        If ``name`` is not a non-empty string.
    InvalidVolumeError
        If ``volume`` is not strictly positive.
    """

    def __init__(self, name: str, volume: float):
        if not isinstance(name, str) or not name.strip():
            raise InvalidNameError(
                "Compartment name must not be empty or whitespace-only."
            )

        if volume <= 0:
            raise InvalidVolumeError("Volume must be greater than zero.")

        self.name = name
        self.volume = volume
        self.inventory = ChemicalInventory()

    def get_quantity(self, molecule: Molecule) -> float:
        """Return the quantity of a molecule in the compartment.

        Parameters
        ----------
        molecule : Molecule
            Molecule whose stored quantity is requested.

        Returns
        -------
        float
            Stored quantity, or ``0.0`` when the molecule is absent.
        """
        return self.inventory.get_quantity(molecule)

    def get_concentration(self, molecule: Molecule) -> float:
        """Calculate the concentration of a molecule.

        Parameters
        ----------
        molecule : Molecule
            Molecule whose concentration is requested.

        Returns
        -------
        float
            Molecule quantity divided by the compartment volume.
        """
        return self.get_quantity(molecule) / self.volume

    def add(self, molecule: Molecule, amount: float) -> None:
        """Add a quantity of a molecule to the compartment.

        Parameters
        ----------
        molecule : Molecule
            Molecule to add.
        amount : float
            Non-negative quantity to add.

        Raises
        ------
        InvalidQuantityError
            If ``amount`` is negative.
        """
        self.inventory.add(molecule, amount)

    def remove(self, molecule: Molecule, amount: float) -> None:
        """Remove a quantity of a molecule from the compartment.

        Parameters
        ----------
        molecule : Molecule
            Molecule to remove.
        amount : float
            Non-negative quantity to remove.

        Raises
        ------
        InvalidQuantityError
            If ``amount`` is negative.
        InsufficientQuantityError
            If the compartment contains less than ``amount``.
        """
        self.inventory.remove(molecule, amount)

    def transfer_to(
        self,
        destination: Compartment,
        molecule: Molecule,
        amount: float,
    ) -> None:
        """Transfer a molecule quantity to another compartment atomically.

        Validation occurs before either compartment is modified. Consequently,
        a failed transfer leaves both compartments unchanged.

        Parameters
        ----------
        destination : Compartment
            Compartment that will receive the molecule.
        molecule : Molecule
            Molecule to transfer.
        amount : float
            Non-negative quantity to transfer.

        Raises
        ------
        ChemistryError
            If ``destination`` is this compartment.
        InvalidQuantityError
            If ``amount`` is negative.
        InsufficientQuantityError
            If this compartment contains less than ``amount``.
        """
        if destination is self:
            raise ChemistryError("A compartment cannot transfer substance to itself.")

        if amount < 0:
            raise InvalidQuantityError("Transfer amount must not be negative.")

        if self.get_quantity(molecule) < amount:
            raise InsufficientQuantityError(
                "Source compartment does not contain enough substance."
            )

        self.remove(molecule, amount)
        destination.add(molecule, amount)
