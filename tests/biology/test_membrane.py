from __future__ import annotations

from collections.abc import Mapping

import pytest

from adam.biology import (
    InvalidMembraneError,
    Membrane,
    MoleculeTransportError,
)
from adam.chemistry.compartment import Compartment
from adam.chemistry.molecule import Molecule
from adam.simulation.exceptions import InvalidTimeStepError
from adam.simulation.process import SimulationProcess


@pytest.fixture
def oxygen() -> Molecule:
    return Molecule("Oxygen", "O2")


@pytest.fixture
def glucose() -> Molecule:
    return Molecule("Glucose", "C6H12O6")


@pytest.fixture
def sodium() -> Molecule:
    return Molecule("Sodium", "Na+")


@pytest.fixture
def inside() -> Compartment:
    return Compartment("Inside", 1.0)


@pytest.fixture
def outside() -> Compartment:
    return Compartment("Outside", 3.0)


@pytest.fixture
def membrane(
    inside: Compartment,
    outside: Compartment,
) -> Membrane:
    return Membrane(inside, outside, area=1.0)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_valid_membrane_can_be_created(
    inside: Compartment,
    outside: Compartment,
) -> None:
    membrane = Membrane(inside, outside, area=2.0)

    assert membrane.inside is inside
    assert membrane.outside is outside
    assert membrane.area == 2.0


def test_membrane_satisfies_simulation_process(
    membrane: Membrane,
) -> None:
    assert isinstance(membrane, SimulationProcess)


def test_same_compartment_on_both_sides_fails() -> None:
    compartment = Compartment("Shared", 1.0)

    with pytest.raises(InvalidMembraneError):
        Membrane(compartment, compartment, area=1.0)


@pytest.mark.parametrize(
    "area",
    [
        0.0,
        -1.0,
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        False,
    ],
)
def test_invalid_area_fails(
    inside: Compartment,
    outside: Compartment,
    area: object,
) -> None:
    with pytest.raises(InvalidMembraneError):
        Membrane(inside, outside, area)  # type: ignore[arg-type]


def test_inside_is_read_only(
    membrane: Membrane,
    outside: Compartment,
) -> None:
    with pytest.raises(AttributeError):
        membrane.inside = outside  # type: ignore[misc]


def test_outside_is_read_only(
    membrane: Membrane,
    inside: Compartment,
) -> None:
    with pytest.raises(AttributeError):
        membrane.outside = inside  # type: ignore[misc]


def test_area_is_read_only(membrane: Membrane) -> None:
    with pytest.raises(AttributeError):
        membrane.area = 5.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Permeability registration
# ---------------------------------------------------------------------------


def test_valid_permeability_can_be_registered(
    membrane: Membrane,
    oxygen: Molecule,
) -> None:
    membrane.set_permeability(oxygen, 0.8)

    assert membrane.get_permeability(oxygen) == 0.8


def test_zero_permeability_is_accepted(
    membrane: Membrane,
    oxygen: Molecule,
) -> None:
    membrane.set_permeability(oxygen, 0.0)

    assert membrane.get_permeability(oxygen) == 0.0


@pytest.mark.parametrize(
    "permeability",
    [
        -1.0,
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        False,
    ],
)
def test_invalid_permeability_fails(
    membrane: Membrane,
    oxygen: Molecule,
    permeability: object,
) -> None:
    with pytest.raises(MoleculeTransportError):
        membrane.set_permeability(
            oxygen,
            permeability,  # type: ignore[arg-type]
        )


def test_non_molecule_key_fails(membrane: Membrane) -> None:
    with pytest.raises(MoleculeTransportError):
        membrane.set_permeability(
            "oxygen",  # type: ignore[arg-type]
            0.8,
        )


def test_replacing_permeability_works(
    membrane: Membrane,
    oxygen: Molecule,
) -> None:
    membrane.set_permeability(oxygen, 0.8)
    membrane.set_permeability(oxygen, 0.2)

    assert membrane.get_permeability(oxygen) == 0.2


def test_replacing_permeability_affects_later_movement(
    membrane: Membrane,
    oxygen: Molecule,
    outside: Compartment,
    inside: Compartment,
) -> None:
    outside.add(oxygen, 12.0)
    membrane.set_permeability(oxygen, 0.1)

    membrane.step(0.1)
    first_transfer = inside.get_quantity(oxygen)

    fresh_inside = Compartment("Fresh Inside", 1.0)
    fresh_outside = Compartment("Fresh Outside", 3.0)
    fresh_outside.add(oxygen, 12.0)

    comparison_membrane = Membrane(
        fresh_inside,
        fresh_outside,
        area=1.0,
    )
    comparison_membrane.set_permeability(oxygen, 0.1)
    comparison_membrane.set_permeability(oxygen, 0.8)

    comparison_membrane.step(0.1)
    second_transfer = fresh_inside.get_quantity(oxygen)

    assert second_transfer > first_transfer


def test_permeabilities_returns_mapping(
    membrane: Membrane,
) -> None:
    assert isinstance(membrane.permeabilities, Mapping)


def test_returned_mapping_cannot_mutate_membrane(
    membrane: Membrane,
    oxygen: Molecule,
) -> None:
    membrane.set_permeability(oxygen, 0.8)

    returned_mapping = dict(membrane.permeabilities)
    returned_mapping[oxygen] = 100.0

    assert membrane.get_permeability(oxygen) == 0.8


# ---------------------------------------------------------------------------
# Lookup and removal
# ---------------------------------------------------------------------------


def test_registered_permeability_can_be_retrieved(
    membrane: Membrane,
    oxygen: Molecule,
) -> None:
    membrane.set_permeability(oxygen, 0.8)

    assert membrane.get_permeability(oxygen) == 0.8


def test_unregistered_lookup_fails(
    membrane: Membrane,
    oxygen: Molecule,
) -> None:
    with pytest.raises(MoleculeTransportError):
        membrane.get_permeability(oxygen)


def test_registered_molecule_can_be_removed(
    membrane: Membrane,
    oxygen: Molecule,
) -> None:
    membrane.set_permeability(oxygen, 0.8)

    membrane.remove_permeability(oxygen)

    assert membrane.is_permeable_to(oxygen) is False


def test_removing_unregistered_molecule_fails(
    membrane: Membrane,
    oxygen: Molecule,
) -> None:
    with pytest.raises(MoleculeTransportError):
        membrane.remove_permeability(oxygen)


def test_positive_registered_permeability_is_permeable(
    membrane: Membrane,
    oxygen: Molecule,
) -> None:
    membrane.set_permeability(oxygen, 0.8)

    assert membrane.is_permeable_to(oxygen) is True


def test_zero_permeability_is_impermeable(
    membrane: Membrane,
    oxygen: Molecule,
) -> None:
    membrane.set_permeability(oxygen, 0.0)

    assert membrane.is_permeable_to(oxygen) is False


def test_unregistered_molecule_is_impermeable(
    membrane: Membrane,
    oxygen: Molecule,
) -> None:
    assert membrane.is_permeable_to(oxygen) is False


# ---------------------------------------------------------------------------
# Transport
# ---------------------------------------------------------------------------


def test_registered_molecule_moves_from_high_to_low_concentration(
    membrane: Membrane,
    oxygen: Molecule,
    outside: Compartment,
    inside: Compartment,
) -> None:
    outside.add(oxygen, 12.0)
    membrane.set_permeability(oxygen, 0.8)

    membrane.step(0.1)

    assert inside.get_quantity(oxygen) > 0.0
    assert outside.get_quantity(oxygen) < 12.0


def test_transport_can_occur_from_outside_to_inside(
    membrane: Membrane,
    oxygen: Molecule,
    outside: Compartment,
    inside: Compartment,
) -> None:
    outside.add(oxygen, 12.0)
    membrane.set_permeability(oxygen, 0.8)

    membrane.step(0.1)

    assert inside.get_quantity(oxygen) > 0.0


def test_transport_can_occur_from_inside_to_outside(
    membrane: Membrane,
    oxygen: Molecule,
    outside: Compartment,
    inside: Compartment,
) -> None:
    inside.add(oxygen, 12.0)
    membrane.set_permeability(oxygen, 0.8)

    membrane.step(0.1)

    assert outside.get_quantity(oxygen) > 0.0


def test_unregistered_molecule_does_not_move(
    membrane: Membrane,
    oxygen: Molecule,
    outside: Compartment,
    inside: Compartment,
) -> None:
    outside.add(oxygen, 12.0)

    membrane.step(0.1)

    assert inside.get_quantity(oxygen) == 0.0
    assert outside.get_quantity(oxygen) == 12.0


def test_zero_permeability_molecule_does_not_move(
    membrane: Membrane,
    sodium: Molecule,
    outside: Compartment,
    inside: Compartment,
) -> None:
    inside.add(sodium, 10.0)
    membrane.set_permeability(sodium, 0.0)

    membrane.step(0.1)

    assert inside.get_quantity(sodium) == 10.0
    assert outside.get_quantity(sodium) == 0.0


def test_multiple_registered_molecules_move_in_one_step(
    membrane: Membrane,
    oxygen: Molecule,
    glucose: Molecule,
    outside: Compartment,
    inside: Compartment,
) -> None:
    outside.add(oxygen, 12.0)
    outside.add(glucose, 12.0)

    membrane.set_permeability(oxygen, 0.8)
    membrane.set_permeability(glucose, 0.1)

    membrane.step(0.1)

    assert inside.get_quantity(oxygen) > 0.0
    assert inside.get_quantity(glucose) > 0.0


def test_changing_one_permeability_does_not_affect_another(
    membrane: Membrane,
    oxygen: Molecule,
    glucose: Molecule,
) -> None:
    membrane.set_permeability(oxygen, 0.8)
    membrane.set_permeability(glucose, 0.1)

    membrane.set_permeability(oxygen, 0.2)

    assert membrane.get_permeability(oxygen) == 0.2
    assert membrane.get_permeability(glucose) == 0.1


def test_total_quantity_of_each_molecule_remains_constant(
    membrane: Membrane,
    oxygen: Molecule,
    glucose: Molecule,
    outside: Compartment,
    inside: Compartment,
) -> None:
    outside.add(oxygen, 12.0)
    inside.add(glucose, 8.0)

    membrane.set_permeability(oxygen, 0.8)
    membrane.set_permeability(glucose, 0.1)

    oxygen_before = inside.get_quantity(oxygen) + outside.get_quantity(oxygen)
    glucose_before = inside.get_quantity(glucose) + outside.get_quantity(glucose)

    membrane.step(0.5)

    oxygen_after = inside.get_quantity(oxygen) + outside.get_quantity(oxygen)
    glucose_after = inside.get_quantity(glucose) + outside.get_quantity(glucose)

    assert oxygen_after == pytest.approx(oxygen_before)
    assert glucose_after == pytest.approx(glucose_before)


def test_transport_does_not_overshoot_equilibrium(
    membrane: Membrane,
    oxygen: Molecule,
    outside: Compartment,
    inside: Compartment,
) -> None:
    outside.add(oxygen, 12.0)
    membrane.set_permeability(oxygen, 100.0)

    membrane.step(100.0)

    assert inside.get_concentration(oxygen) == pytest.approx(3.0)
    assert outside.get_concentration(oxygen) == pytest.approx(3.0)


def test_large_step_reaches_equilibrium_without_oscillation(
    membrane: Membrane,
    oxygen: Molecule,
    outside: Compartment,
    inside: Compartment,
) -> None:
    outside.add(oxygen, 12.0)
    membrane.set_permeability(oxygen, 100.0)

    membrane.step(100.0)
    inside_after_first_step = inside.get_quantity(oxygen)
    outside_after_first_step = outside.get_quantity(oxygen)

    membrane.step(100.0)

    assert inside.get_quantity(oxygen) == pytest.approx(inside_after_first_step)
    assert outside.get_quantity(oxygen) == pytest.approx(outside_after_first_step)


def test_unequal_volumes_produce_correct_equilibrium(
    membrane: Membrane,
    oxygen: Molecule,
    outside: Compartment,
    inside: Compartment,
) -> None:
    outside.add(oxygen, 12.0)
    membrane.set_permeability(oxygen, 100.0)

    membrane.step(100.0)

    expected_concentration = 12.0 / 4.0

    assert inside.get_concentration(oxygen) == pytest.approx(expected_concentration)
    assert outside.get_concentration(oxygen) == pytest.approx(expected_concentration)
    assert inside.get_quantity(oxygen) == pytest.approx(3.0)
    assert outside.get_quantity(oxygen) == pytest.approx(9.0)


def test_repeated_steps_approach_equilibrium(
    membrane: Membrane,
    oxygen: Molecule,
    outside: Compartment,
    inside: Compartment,
) -> None:
    outside.add(oxygen, 12.0)
    membrane.set_permeability(oxygen, 0.1)

    initial_difference = abs(
        inside.get_concentration(oxygen) - outside.get_concentration(oxygen)
    )

    for _ in range(20):
        membrane.step(0.1)

    final_difference = abs(
        inside.get_concentration(oxygen) - outside.get_concentration(oxygen)
    )

    assert final_difference < initial_difference


# ---------------------------------------------------------------------------
# Failure and ordering
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "delta_time",
    [
        0.0,
        -1.0,
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        False,
    ],
)
def test_invalid_delta_time_causes_no_movement(
    membrane: Membrane,
    oxygen: Molecule,
    glucose: Molecule,
    outside: Compartment,
    inside: Compartment,
    delta_time: object,
) -> None:
    outside.add(oxygen, 12.0)
    outside.add(glucose, 12.0)

    membrane.set_permeability(oxygen, 0.8)
    membrane.set_permeability(glucose, 0.1)

    with pytest.raises(InvalidTimeStepError):
        membrane.step(delta_time)  # type: ignore[arg-type]

    assert inside.get_quantity(oxygen) == 0.0
    assert outside.get_quantity(oxygen) == 12.0
    assert inside.get_quantity(glucose) == 0.0
    assert outside.get_quantity(glucose) == 12.0


def test_molecules_are_stored_in_registration_order(
    membrane: Membrane,
    oxygen: Molecule,
    glucose: Molecule,
    sodium: Molecule,
) -> None:
    membrane.set_permeability(oxygen, 0.8)
    membrane.set_permeability(glucose, 0.1)
    membrane.set_permeability(sodium, 0.0)

    assert list(membrane.permeabilities) == [
        oxygen,
        glucose,
        sodium,
    ]


def test_replacing_permeability_preserves_order(
    membrane: Membrane,
    oxygen: Molecule,
    glucose: Molecule,
    sodium: Molecule,
) -> None:
    membrane.set_permeability(oxygen, 0.8)
    membrane.set_permeability(glucose, 0.1)
    membrane.set_permeability(sodium, 0.0)

    membrane.set_permeability(glucose, 0.5)

    assert list(membrane.permeabilities) == [
        oxygen,
        glucose,
        sodium,
    ]


def test_removal_and_reregistration_moves_molecule_to_end(
    membrane: Membrane,
    oxygen: Molecule,
    glucose: Molecule,
    sodium: Molecule,
) -> None:
    membrane.set_permeability(oxygen, 0.8)
    membrane.set_permeability(glucose, 0.1)
    membrane.set_permeability(sodium, 0.0)

    membrane.remove_permeability(glucose)
    membrane.set_permeability(glucose, 0.2)

    assert list(membrane.permeabilities) == [
        oxygen,
        sodium,
        glucose,
    ]
