from __future__ import annotations

import math

from adam.chemistry.compartment import Compartment
from adam.chemistry.exceptions import InvalidDiffusionError
from adam.chemistry.molecule import Molecule
from adam.simulation.clock import SimulationClock


class PassiveDiffusion:
    """Moves one molecule between two compartments down its concentration gradient."""

    _TOLERANCE = 1e-12

    def __init__(
        self,
        molecule: Molecule,
        compartment_a: Compartment,
        compartment_b: Compartment,
        permeability: float,
        area: float,
    ) -> None:
        if compartment_a is compartment_b:
            raise InvalidDiffusionError(
                "Diffusion compartments must be different objects."
            )

        self._validate_non_negative_finite(
            permeability,
            name="permeability",
        )
        self._validate_positive_finite(area, name="area")

        self.molecule = molecule
        self.compartment_a = compartment_a
        self.compartment_b = compartment_b
        self.permeability = float(permeability)
        self.area = float(area)

    @staticmethod
    def _validate_non_negative_finite(value: float, *, name: str) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidDiffusionError(f"{name} must be a real number.")
        if not math.isfinite(value):
            raise InvalidDiffusionError(f"{name} must be finite.")
        if value < 0:
            raise InvalidDiffusionError(f"{name} must be non-negative.")

    @staticmethod
    def _validate_positive_finite(value: float, *, name: str) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidDiffusionError(f"{name} must be a real number.")
        if not math.isfinite(value):
            raise InvalidDiffusionError(f"{name} must be finite.")
        if value <= 0:
            raise InvalidDiffusionError(f"{name} must be strictly positive.")

    def step(self, delta_time: float) -> None:
        """Perform one passive-diffusion time step."""
        SimulationClock.validate_delta_time(delta_time)

        concentration_a = self.compartment_a.get_concentration(self.molecule)
        concentration_b = self.compartment_b.get_concentration(self.molecule)
        difference = concentration_a - concentration_b

        if math.isclose(
            difference,
            0.0,
            rel_tol=self._TOLERANCE,
            abs_tol=self._TOLERANCE,
        ):
            return

        if difference > 0:
            source = self.compartment_a
            destination = self.compartment_b
        else:
            source = self.compartment_b
            destination = self.compartment_a

        quantity_a = self.compartment_a.get_quantity(self.molecule)
        quantity_b = self.compartment_b.get_quantity(self.molecule)
        volume_a = self.compartment_a.volume
        volume_b = self.compartment_b.volume

        equilibrium_concentration = (quantity_a + quantity_b) / (volume_a + volume_b)

        source_quantity = source.get_quantity(self.molecule)
        maximum_transfer = source_quantity - equilibrium_concentration * source.volume

        if maximum_transfer <= self._TOLERANCE:
            return

        flux_magnitude = self.permeability * self.area * abs(difference)
        requested_transfer = flux_magnitude * float(delta_time)
        actual_transfer = min(requested_transfer, maximum_transfer)

        if actual_transfer <= self._TOLERANCE:
            return

        source.transfer_to(
            destination,
            self.molecule,
            actual_transfer,
        )
