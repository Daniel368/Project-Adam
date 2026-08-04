from __future__ import annotations

import math

import pytest

from adam.chemistry.compartment import Compartment
from adam.chemistry.diffusion import PassiveDiffusion
from adam.chemistry.exceptions import InvalidDiffusionError
from adam.chemistry.molecule import Molecule
from adam.simulation.exceptions import InvalidTimeStepError


@pytest.fixture
def glucose() -> Molecule:
    return Molecule(name="Glucose", symbol="C6H12O6")


def make_compartments(
    glucose: Molecule,
    *,
    quantity_a: float = 10.0,
    quantity_b: float = 0.0,
    volume_a: float = 1.0,
    volume_b: float = 1.0,
) -> tuple[Compartment, Compartment]:
    a = Compartment("A", volume_a)
    b = Compartment("B", volume_b)
    a.add(glucose, quantity_a)
    b.add(glucose, quantity_b)
    return a, b


def test_valid_diffusion_can_be_created(glucose: Molecule) -> None:
    a, b = make_compartments(glucose)
    diffusion = PassiveDiffusion(glucose, a, b, 0.5, 1.0)
    assert diffusion.molecule == glucose


def test_same_compartment_fails(glucose: Molecule) -> None:
    a, _ = make_compartments(glucose)
    with pytest.raises(InvalidDiffusionError):
        PassiveDiffusion(glucose, a, a, 0.5, 1.0)


@pytest.mark.parametrize("permeability", [-1.0, math.nan, math.inf, -math.inf, True])
def test_invalid_permeability_fails(
    glucose: Molecule,
    permeability: float,
) -> None:
    a, b = make_compartments(glucose)
    with pytest.raises(InvalidDiffusionError):
        PassiveDiffusion(glucose, a, b, permeability, 1.0)


def test_zero_permeability_is_allowed(glucose: Molecule) -> None:
    a, b = make_compartments(glucose)
    PassiveDiffusion(glucose, a, b, 0.0, 1.0)


@pytest.mark.parametrize("area", [0.0, -1.0, math.nan, math.inf, -math.inf, True])
def test_invalid_area_fails(glucose: Molecule, area: float) -> None:
    a, b = make_compartments(glucose)
    with pytest.raises(InvalidDiffusionError):
        PassiveDiffusion(glucose, a, b, 0.5, area)


@pytest.mark.parametrize("delta_time", [0.0, -1.0])
def test_invalid_delta_time_fails(
    glucose: Molecule,
    delta_time: float,
) -> None:
    a, b = make_compartments(glucose)
    diffusion = PassiveDiffusion(glucose, a, b, 0.5, 1.0)

    with pytest.raises(InvalidTimeStepError):
        diffusion.step(delta_time)


def test_moves_from_high_to_low_concentration(glucose: Molecule) -> None:
    a, b = make_compartments(glucose)
    diffusion = PassiveDiffusion(glucose, a, b, 0.5, 1.0)

    diffusion.step(0.1)

    assert a.get_quantity(glucose) < 10.0
    assert b.get_quantity(glucose) > 0.0


def test_direction_reverses(glucose: Molecule) -> None:
    a, b = make_compartments(glucose, quantity_a=0.0, quantity_b=10.0)
    diffusion = PassiveDiffusion(glucose, a, b, 0.5, 1.0)

    diffusion.step(0.1)

    assert a.get_quantity(glucose) > 0.0
    assert b.get_quantity(glucose) < 10.0


def test_equal_concentrations_cause_no_movement(glucose: Molecule) -> None:
    a, b = make_compartments(glucose, quantity_a=5.0, quantity_b=5.0)
    diffusion = PassiveDiffusion(glucose, a, b, 0.5, 1.0)

    diffusion.step(1.0)

    assert a.get_quantity(glucose) == pytest.approx(5.0)
    assert b.get_quantity(glucose) == pytest.approx(5.0)


def test_zero_permeability_causes_no_movement(glucose: Molecule) -> None:
    a, b = make_compartments(glucose)
    diffusion = PassiveDiffusion(glucose, a, b, 0.0, 1.0)

    diffusion.step(1.0)

    assert a.get_quantity(glucose) == pytest.approx(10.0)
    assert b.get_quantity(glucose) == pytest.approx(0.0)


def test_total_quantity_is_conserved(glucose: Molecule) -> None:
    a, b = make_compartments(glucose)
    diffusion = PassiveDiffusion(glucose, a, b, 0.5, 1.0)
    before = a.get_quantity(glucose) + b.get_quantity(glucose)

    diffusion.step(0.5)

    after = a.get_quantity(glucose) + b.get_quantity(glucose)
    assert after == pytest.approx(before)


def test_does_not_overshoot_equilibrium(glucose: Molecule) -> None:
    a, b = make_compartments(glucose)
    diffusion = PassiveDiffusion(glucose, a, b, 1000.0, 1.0)

    diffusion.step(1000.0)

    assert a.get_concentration(glucose) >= b.get_concentration(glucose)
    assert a.get_concentration(glucose) == pytest.approx(b.get_concentration(glucose))


def test_large_step_reaches_equilibrium(glucose: Molecule) -> None:
    a, b = make_compartments(glucose)
    diffusion = PassiveDiffusion(glucose, a, b, 1000.0, 1.0)

    diffusion.step(1000.0)

    assert a.get_concentration(glucose) == pytest.approx(5.0)
    assert b.get_concentration(glucose) == pytest.approx(5.0)


def test_repeated_steps_approach_equilibrium(glucose: Molecule) -> None:
    a, b = make_compartments(glucose)
    diffusion = PassiveDiffusion(glucose, a, b, 0.25, 1.0)
    initial_difference = abs(
        a.get_concentration(glucose) - b.get_concentration(glucose)
    )

    for _ in range(20):
        diffusion.step(0.1)

    final_difference = abs(a.get_concentration(glucose) - b.get_concentration(glucose))
    assert final_difference < initial_difference


def test_no_oscillation_after_equilibrium(glucose: Molecule) -> None:
    a, b = make_compartments(glucose)
    diffusion = PassiveDiffusion(glucose, a, b, 1000.0, 1.0)
    diffusion.step(1000.0)
    equilibrium_a = a.get_quantity(glucose)
    equilibrium_b = b.get_quantity(glucose)

    for _ in range(10):
        diffusion.step(1.0)

    assert a.get_quantity(glucose) == pytest.approx(equilibrium_a)
    assert b.get_quantity(glucose) == pytest.approx(equilibrium_b)


def test_unequal_volumes_have_correct_equilibrium(glucose: Molecule) -> None:
    a, b = make_compartments(
        glucose,
        quantity_a=10.0,
        quantity_b=0.0,
        volume_a=1.0,
        volume_b=3.0,
    )
    diffusion = PassiveDiffusion(glucose, a, b, 1000.0, 1.0)

    diffusion.step(1000.0)

    assert a.get_concentration(glucose) == pytest.approx(2.5)
    assert b.get_concentration(glucose) == pytest.approx(2.5)
    assert a.get_quantity(glucose) == pytest.approx(2.5)
    assert b.get_quantity(glucose) == pytest.approx(7.5)


def test_failed_diffusion_leaves_both_unchanged(glucose: Molecule) -> None:
    a, b = make_compartments(glucose)
    diffusion = PassiveDiffusion(glucose, a, b, 0.5, 1.0)
    before_a = a.get_quantity(glucose)
    before_b = b.get_quantity(glucose)

    with pytest.raises(InvalidTimeStepError):
        diffusion.step(0.0)

    assert a.get_quantity(glucose) == pytest.approx(before_a)
    assert b.get_quantity(glucose) == pytest.approx(before_b)
