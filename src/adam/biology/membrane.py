from __future__ import annotations

import math
from collections.abc import Mapping

from adam.chemistry import Compartment, Molecule, PassiveDiffusion
from adam.simulation import SimulationClock

from .exceptions import InvalidMembraneError, MoleculeTransportError


class Membrane:
    """A selective boundary between two chemical compartments.

    Molecules are transported in their registration order. Replacing an
    existing permeability preserves that molecule's position. Removing
    and re-registering it places it at the end.
    """

    def __init__(
        self,
        inside: Compartment,
        outside: Compartment,
        area: float,
    ) -> None:
        if inside is outside:
            raise InvalidMembraneError(
                "Inside and outside must be different compartments."
            )

        if isinstance(area, bool) or not isinstance(area, (int, float)):
            raise InvalidMembraneError("Membrane area must be a numeric value.")

        if not math.isfinite(area):
            raise InvalidMembraneError("Membrane area must be finite.")

        if area <= 0:
            raise InvalidMembraneError("Membrane area must be strictly positive.")

        self._inside = inside
        self._outside = outside
        self._area = float(area)
        self._permeabilities: dict[Molecule, float] = {}

    @property
    def inside(self) -> Compartment:
        return self._inside

    @property
    def outside(self) -> Compartment:
        return self._outside

    @property
    def area(self) -> float:
        return self._area

    @property
    def permeabilities(self) -> Mapping[Molecule, float]:
        return self._permeabilities.copy()

    def set_permeability(
        self,
        molecule: Molecule,
        permeability: float,
    ) -> None:
        if not isinstance(molecule, Molecule):
            raise MoleculeTransportError(
                "Permeability can only be registered for a Molecule."
            )

        if isinstance(permeability, bool) or not isinstance(
            permeability,
            (int, float),
        ):
            raise MoleculeTransportError("Permeability must be a numeric value.")

        if not math.isfinite(permeability):
            raise MoleculeTransportError("Permeability must be finite.")

        if permeability < 0:
            raise MoleculeTransportError("Permeability must be non-negative.")

        self._permeabilities[molecule] = float(permeability)

    def remove_permeability(self, molecule: Molecule) -> None:
        if not isinstance(molecule, Molecule):
            raise MoleculeTransportError(
                "Permeability can only be removed for a Molecule."
            )

        if molecule not in self._permeabilities:
            raise MoleculeTransportError(
                "The molecule is not registered with this membrane."
            )

        del self._permeabilities[molecule]

    def get_permeability(self, molecule: Molecule) -> float:
        if not isinstance(molecule, Molecule):
            raise MoleculeTransportError(
                "Permeability can only be retrieved for a Molecule."
            )

        if molecule not in self._permeabilities:
            raise MoleculeTransportError(
                "The molecule is not registered with this membrane."
            )

        return self._permeabilities[molecule]

    def is_permeable_to(self, molecule: Molecule) -> bool:
        return self._permeabilities.get(molecule, 0.0) > 0.0

    def step(self, delta_time: float) -> None:
        """Advance configured transports in registration order."""
        SimulationClock.validate_delta_time(delta_time)

        for molecule, permeability in self._permeabilities.items():
            if permeability == 0.0:
                continue

            diffusion = PassiveDiffusion(
                molecule=molecule,
                compartment_a=self._inside,
                compartment_b=self._outside,
                permeability=permeability,
                area=self._area,
            )

            diffusion.step(delta_time)
