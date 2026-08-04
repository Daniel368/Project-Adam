"""Define and execute fixed stoichiometric reactions."""

import math
from collections.abc import Mapping
from types import MappingProxyType

from adam.chemistry.compartment import Compartment
from adam.chemistry.exceptions import (
    InsufficientQuantityError,
    InvalidQuantityError,
    InvalidReactionError,
)
from adam.chemistry.molecule import Molecule


class Reaction:
    """A fixed stoichiometric reaction.

    Parameters
    ----------
    name : str
        Human-readable reaction name.
    reactants : dict[Molecule, float]
        Mapping from each reactant molecule to its strictly positive
        stoichiometric coefficient.
    products : dict[Molecule, float]
        Mapping from each product molecule to its strictly positive
        stoichiometric coefficient.

    Attributes
    ----------
    name : str
        Reaction name.
    reactants : MappingProxyType
        Read-only reactant-to-coefficient mapping.
    products : MappingProxyType
        Read-only product-to-coefficient mapping.

    Raises
    ------
    InvalidReactionError
        If the name, mappings, or coefficients are invalid.

    Notes
    -----
    Input mappings are defensively copied and then exposed through read-only
    proxies. Zero extent is allowed and performs no changes; negative extent
    is rejected. Quantities are consumed and produced exactly according to the
    declared stoichiometric coefficients. The engine does not yet verify
    elemental or mass conservation.
    """

    def __init__(
        self,
        name: str,
        reactants: Mapping[Molecule, float],
        products: Mapping[Molecule, float],
    ) -> None:
        self._validate_name(name)
        self._validate_mapping(reactants, "reactants")
        self._validate_mapping(products, "products")

        self._name = name

        reactants_copy = dict(reactants)
        products_copy = dict(products)

        self._reactants = MappingProxyType(reactants_copy)
        self._products = MappingProxyType(products_copy)

    @property
    def name(self) -> str:
        """Return the reaction name.

        Returns
        -------
        str
            Human-readable reaction name.
        """
        return self._name

    @property
    def reactants(self) -> Mapping[Molecule, float]:
        """Return the read-only reactant mapping.

        Returns
        -------
        MappingProxyType
            Molecule-to-coefficient mapping that cannot be mutated.
        """
        return self._reactants

    @property
    def products(self) -> Mapping[Molecule, float]:
        """Return the read-only product mapping.

        Returns
        -------
        MappingProxyType
            Molecule-to-coefficient mapping that cannot be mutated.
        """
        return self._products

    def maximum_extent(self, compartment: Compartment) -> float:
        """Calculate the greatest reaction extent currently possible.

        Parameters
        ----------
        compartment : Compartment
            Compartment containing the available reactants.

        Returns
        -------
        float
            Minimum ratio of available quantity to required coefficient across
            all reactants.
        """
        possible_extents = []

        for molecule, coefficient in self._reactants.items():
            available_amount = compartment.get_quantity(molecule)
            possible_extent = available_amount / coefficient
            possible_extents.append(possible_extent)

        return min(possible_extents)

    def can_execute(self, compartment: Compartment, extent: float) -> bool:
        """Check whether a requested reaction extent can be executed.

        Parameters
        ----------
        compartment : Compartment
            Compartment containing the reactants.
        extent : float
            Non-negative number of reaction units requested.

        Returns
        -------
        bool
            ``True`` if every reactant is sufficiently available; otherwise
            ``False``.

        Raises
        ------
        InvalidQuantityError
            If ``extent`` is not numeric or is negative.
        """
        self._validate_extent(extent)

        required_reactants = self._calculate_required_reactants(extent)

        for molecule, required_amount in required_reactants.items():
            available_amount = compartment.get_quantity(molecule)

            if available_amount < required_amount:
                return False

        return True

    def execute(self, compartment: Compartment, extent: float = 1.0) -> None:
        """Execute the reaction within a compartment.

        All required quantities are calculated and validated before any state
        change occurs. An execution that fails because of insufficient
        reactants therefore leaves the compartment unchanged.

        Parameters
        ----------
        compartment : Compartment
            Compartment whose inventory will be modified.
        extent : float
            Non-negative number of reaction units to execute, by default
            ``1.0``.

        Raises
        ------
        InvalidQuantityError
            If ``extent`` is not numeric or is negative.
        InsufficientQuantityError
            If any reactant quantity is insufficient.
        """
        self._validate_extent(extent)

        if extent == 0:
            return

        required_reactants = self._calculate_required_reactants(extent)
        produced_products = self._calculate_produced_products(extent)

        for molecule, required_amount in required_reactants.items():
            available_amount = compartment.get_quantity(molecule)

            if available_amount < required_amount:
                raise InsufficientQuantityError(
                    f"Not enough {molecule}. "
                    f"Required: {required_amount}, "
                    f"available: {available_amount}"
                )

        for molecule, required_amount in required_reactants.items():
            compartment.remove(molecule, required_amount)

        for molecule, produced_amount in produced_products.items():
            compartment.add(molecule, produced_amount)

    def _calculate_required_reactants(self, extent: float) -> dict[Molecule, float]:
        """Calculate reactant quantities required for an extent.

        Parameters
        ----------
        extent : float
            Number of reaction units.

        Returns
        -------
        dict[Molecule, float]
            Required quantity for each reactant.
        """
        required_reactants = {}

        for molecule, coefficient in self._reactants.items():
            required_amount = coefficient * extent
            required_reactants[molecule] = required_amount

        return required_reactants

    def _calculate_produced_products(self, extent: float) -> dict[Molecule, float]:
        """Calculate product quantities generated for an extent.

        Parameters
        ----------
        extent : float
            Number of reaction units.

        Returns
        -------
        dict[Molecule, float]
            Produced quantity for each product.
        """
        produced_products = {}

        for molecule, coefficient in self._products.items():
            produced_amount = coefficient * extent
            produced_products[molecule] = produced_amount

        return produced_products

    @staticmethod
    def _validate_name(name: str) -> None:
        """Validate a reaction name.

        Parameters
        ----------
        name : str
            Candidate reaction name.

        Raises
        ------
        InvalidReactionError
            If ``name`` is not a non-empty string.
        """
        if not isinstance(name, str):
            raise InvalidReactionError("Reaction name must be a string")

        if name.strip() == "":
            raise InvalidReactionError(
                "Reaction name cannot be empty or whitespace only"
            )

    @staticmethod
    def _validate_mapping(mapping: Mapping[Molecule, float], mapping_name: str) -> None:
        """Validate a reactant or product coefficient mapping.

        Parameters
        ----------
        mapping : dict
            Mapping to validate.
        mapping_name : str
            Human-readable mapping name used in error messages.

        Raises
        ------
        InvalidReactionError
            If the mapping is not a non-empty dictionary or contains a
            non-numeric, Boolean, non-finite, zero, or negative coefficient.
        """
        if not isinstance(mapping, Mapping):
            raise InvalidReactionError(
                f"{mapping_name.capitalize()} must be a dictionary"
            )

        if len(mapping) == 0:
            raise InvalidReactionError(
                f"A reaction must have at least one {mapping_name[:-1]}"
            )

        for molecule, coefficient in mapping.items():
            if (
                isinstance(coefficient, bool)
                or not isinstance(coefficient, (int, float))
                or not math.isfinite(coefficient)
                or coefficient <= 0
            ):
                raise InvalidReactionError(
                    f"Coefficient for {molecule} must be a finite, "
                    "strictly positive number"
                )

    @staticmethod
    def _validate_extent(extent: float) -> None:
        """Validate a requested reaction extent.

        Parameters
        ----------
        extent : float
            Candidate extent.

        Raises
        ------
        InvalidQuantityError
            If ``extent`` is Boolean, non-numeric, non-finite, or negative.
        """
        if (
            isinstance(extent, bool)
            or not isinstance(extent, (int, float))
            or not math.isfinite(extent)
            or extent < 0
        ):
            raise InvalidQuantityError(
                "Reaction extent must be a finite, non-negative number"
            )
