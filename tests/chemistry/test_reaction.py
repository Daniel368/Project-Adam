"""Tests for stoichiometric reaction validation and execution."""

import pytest

from adam.chemistry.compartment import Compartment
from adam.chemistry.molecule import Molecule
from adam.chemistry.reaction import Reaction
from adam.chemistry.exceptions import (
    InvalidQuantityError,
    InvalidReactionError,
    InsufficientQuantityError,
)


def test_valid_reaction_can_be_created():
    """Valid reaction can be created."""
    hydrogen = Molecule("Hydrogen", "H2")
    oxygen = Molecule("Oxygen", "O2")
    water = Molecule("Water", "H2O")

    reaction = Reaction(
        name="Water formation",
        reactants={
            hydrogen: 2.0,
            oxygen: 1.0,
        },
        products={
            water: 2.0,
        },
    )

    assert reaction.name == "Water formation"
    assert reaction.reactants == {
        hydrogen: 2.0,
        oxygen: 1.0,
    }
    assert reaction.products == {
        water: 2.0,
    }


def test_empty_reactants_fail():
    """Empty reactants fail."""
    water = Molecule("Water", "H2O")

    with pytest.raises(InvalidReactionError):
        Reaction(
            name="Invalid reaction",
            reactants={},
            products={water: 1.0},
        )


def test_empty_products_fail():
    """Empty products fail."""
    hydrogen = Molecule("Hydrogen", "H2")

    with pytest.raises(InvalidReactionError):
        Reaction(
            name="Invalid reaction",
            reactants={hydrogen: 1.0},
            products={},
        )


def test_zero_reactant_coefficient_fails():
    """Zero reactant coefficient raises the expected error."""
    hydrogen = Molecule("Hydrogen", "H2")
    water = Molecule("Water", "H2O")

    with pytest.raises(InvalidReactionError):
        Reaction(
            name="Invalid reaction",
            reactants={hydrogen: 0.0},
            products={water: 1.0},
        )


def test_zero_product_coefficient_fails():
    """Zero product coefficient raises the expected error."""
    hydrogen = Molecule("Hydrogen", "H2")
    water = Molecule("Water", "H2O")

    with pytest.raises(InvalidReactionError):
        Reaction(
            name="Invalid reaction",
            reactants={hydrogen: 1.0},
            products={water: 0.0},
        )


def test_negative_reactant_coefficient_fails():
    """Negative reactant coefficient raises the expected error."""
    hydrogen = Molecule("Hydrogen", "H2")
    water = Molecule("Water", "H2O")

    with pytest.raises(InvalidReactionError):
        Reaction(
            name="Invalid reaction",
            reactants={hydrogen: -2.0},
            products={water: 1.0},
        )


def test_negative_product_coefficient_fails():
    """Negative product coefficient raises the expected error."""
    hydrogen = Molecule("Hydrogen", "H2")
    water = Molecule("Water", "H2O")

    with pytest.raises(InvalidReactionError):
        Reaction(
            name="Invalid reaction",
            reactants={hydrogen: 1.0},
            products={water: -2.0},
        )


def test_maximum_extent_is_correct():
    """Maximum extent is correct."""
    hydrogen = Molecule("Hydrogen", "H2")
    oxygen = Molecule("Oxygen", "O2")
    water = Molecule("Water", "H2O")

    reaction = Reaction(
        name="Water formation",
        reactants={
            hydrogen: 2.0,
            oxygen: 1.0,
        },
        products={
            water: 2.0,
        },
    )

    compartment = Compartment("Reaction chamber", 10.0)
    compartment.add(hydrogen, 10.0)
    compartment.add(oxygen, 3.0)

    assert reaction.maximum_extent(compartment) == pytest.approx(3.0)


def test_execution_consumes_correct_reactant_amounts():
    """Execution consumes correct reactant amounts."""
    hydrogen = Molecule("Hydrogen", "H2")
    oxygen = Molecule("Oxygen", "O2")
    water = Molecule("Water", "H2O")

    reaction = Reaction(
        name="Water formation",
        reactants={
            hydrogen: 2.0,
            oxygen: 1.0,
        },
        products={
            water: 2.0,
        },
    )

    compartment = Compartment("Reaction chamber", 10.0)
    compartment.add(hydrogen, 10.0)
    compartment.add(oxygen, 5.0)

    reaction.execute(compartment, extent=2.0)

    assert compartment.get_quantity(hydrogen) == pytest.approx(6.0)
    assert compartment.get_quantity(oxygen) == pytest.approx(3.0)


def test_execution_creates_correct_product_amounts():
    """Execution creates correct product amounts."""
    hydrogen = Molecule("Hydrogen", "H2")
    oxygen = Molecule("Oxygen", "O2")
    water = Molecule("Water", "H2O")

    reaction = Reaction(
        name="Water formation",
        reactants={
            hydrogen: 2.0,
            oxygen: 1.0,
        },
        products={
            water: 2.0,
        },
    )

    compartment = Compartment("Reaction chamber", 10.0)
    compartment.add(hydrogen, 10.0)
    compartment.add(oxygen, 5.0)

    reaction.execute(compartment, extent=2.0)

    assert compartment.get_quantity(water) == pytest.approx(4.0)


def test_products_are_added_to_existing_quantity():
    """Products are added to existing quantity."""
    hydrogen = Molecule("Hydrogen", "H2")
    oxygen = Molecule("Oxygen", "O2")
    water = Molecule("Water", "H2O")

    reaction = Reaction(
        name="Water formation",
        reactants={
            hydrogen: 2.0,
            oxygen: 1.0,
        },
        products={
            water: 2.0,
        },
    )

    compartment = Compartment("Reaction chamber", 10.0)
    compartment.add(hydrogen, 10.0)
    compartment.add(oxygen, 5.0)
    compartment.add(water, 3.0)

    reaction.execute(compartment, extent=2.0)

    assert compartment.get_quantity(water) == pytest.approx(7.0)


def test_insufficient_reactants_cause_no_state_changes():
    """Insufficient reactants cause no state changes."""
    hydrogen = Molecule("Hydrogen", "H2")
    oxygen = Molecule("Oxygen", "O2")
    water = Molecule("Water", "H2O")

    reaction = Reaction(
        name="Water formation",
        reactants={
            hydrogen: 2.0,
            oxygen: 1.0,
        },
        products={
            water: 2.0,
        },
    )

    compartment = Compartment("Reaction chamber", 10.0)
    compartment.add(hydrogen, 10.0)
    compartment.add(oxygen, 1.0)
    compartment.add(water, 3.0)

    with pytest.raises(InsufficientQuantityError):
        reaction.execute(compartment, extent=2.0)

    assert compartment.get_quantity(hydrogen) == pytest.approx(10.0)
    assert compartment.get_quantity(oxygen) == pytest.approx(1.0)
    assert compartment.get_quantity(water) == pytest.approx(3.0)


def test_negative_extent_fails():
    """Negative extent raises the expected error."""
    hydrogen = Molecule("Hydrogen", "H2")
    water = Molecule("Water", "H2O")

    reaction = Reaction(
        name="Water formation",
        reactants={hydrogen: 1.0},
        products={water: 1.0},
    )

    compartment = Compartment("Reaction chamber", 10.0)
    compartment.add(hydrogen, 10.0)

    with pytest.raises(InvalidQuantityError):
        reaction.execute(compartment, extent=-1.0)


def test_negative_extent_leaves_compartment_unchanged():
    """Negative extent leaves compartment unchanged."""
    hydrogen = Molecule("Hydrogen", "H2")
    water = Molecule("Water", "H2O")

    reaction = Reaction(
        name="Water formation",
        reactants={hydrogen: 1.0},
        products={water: 1.0},
    )

    compartment = Compartment("Reaction chamber", 10.0)
    compartment.add(hydrogen, 10.0)

    with pytest.raises(InvalidQuantityError):
        reaction.execute(compartment, extent=-1.0)

    assert compartment.get_quantity(hydrogen) == pytest.approx(10.0)
    assert compartment.get_quantity(water) == 0.0


def test_input_reactant_mapping_cannot_mutate_reaction():
    """Input reactant mapping cannot mutate reaction."""
    hydrogen = Molecule("Hydrogen", "H2")
    oxygen = Molecule("Oxygen", "O2")
    water = Molecule("Water", "H2O")

    reactants = {
        hydrogen: 2.0,
        oxygen: 1.0,
    }

    reaction = Reaction(
        name="Water formation",
        reactants=reactants,
        products={water: 2.0},
    )

    reactants[hydrogen] = 100.0
    reactants.clear()

    assert reaction.reactants == {
        hydrogen: 2.0,
        oxygen: 1.0,
    }


def test_input_product_mapping_cannot_mutate_reaction():
    """Input product mapping cannot mutate reaction."""
    hydrogen = Molecule("Hydrogen", "H2")
    water = Molecule("Water", "H2O")

    products = {
        water: 2.0,
    }

    reaction = Reaction(
        name="Water formation",
        reactants={hydrogen: 2.0},
        products=products,
    )

    products[water] = 100.0
    products.clear()

    assert reaction.products == {
        water: 2.0,
    }


def test_returned_reactant_mapping_is_read_only():
    """Returned reactant mapping is read only."""
    hydrogen = Molecule("Hydrogen", "H2")
    water = Molecule("Water", "H2O")

    reaction = Reaction(
        name="Water formation",
        reactants={hydrogen: 2.0},
        products={water: 1.0},
    )

    with pytest.raises(TypeError):
        reaction.reactants[hydrogen] = 100.0


def test_returned_product_mapping_is_read_only():
    """Returned product mapping is read only."""
    hydrogen = Molecule("Hydrogen", "H2")
    water = Molecule("Water", "H2O")

    reaction = Reaction(
        name="Water formation",
        reactants={hydrogen: 2.0},
        products={water: 1.0},
    )

    with pytest.raises(TypeError):
        reaction.products[water] = 100.0


@pytest.mark.parametrize("invalid_coefficient", [float("nan"), float("inf"), float("-inf"), True, False])
def test_reaction_rejects_non_finite_coefficients_and_booleans(invalid_coefficient):
    """Reaction coefficients reject non-finite values and Boolean values."""
    hydrogen = Molecule("Hydrogen", "H2")
    water = Molecule("Water", "H2O")

    with pytest.raises(InvalidReactionError):
        Reaction(
            name="Invalid reaction",
            reactants={hydrogen: invalid_coefficient},
            products={water: 1.0},
        )


@pytest.mark.parametrize("invalid_extent", [float("nan"), float("inf"), float("-inf"), True, False])
def test_reaction_rejects_non_finite_extents_and_booleans(invalid_extent):
    """Reaction extents reject non-finite values and Boolean values."""
    hydrogen = Molecule("Hydrogen", "H2")
    water = Molecule("Water", "H2O")
    reaction = Reaction(
        name="Water formation",
        reactants={hydrogen: 1.0},
        products={water: 1.0},
    )
    compartment = Compartment("Reaction chamber", 10.0)
    compartment.add(hydrogen, 10.0)

    with pytest.raises(InvalidQuantityError):
        reaction.execute(compartment, extent=invalid_extent)

    assert compartment.get_quantity(hydrogen) == 10.0
    assert compartment.get_quantity(water) == 0.0
