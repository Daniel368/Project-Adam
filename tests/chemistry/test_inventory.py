"""Tests for chemical inventory quantity operations."""

import pytest

from adam.chemistry.exceptions import (
    InsufficientQuantityError,
    InvalidQuantityError,
)
from adam.chemistry.inventory import ChemicalInventory
from adam.chemistry.molecule import Molecule


def test_missing_molecules():
    """Missing molecules."""
    water = Molecule("Water", "H2O")
    inventory = ChemicalInventory()

    assert inventory.get_quantity(water) == 0.0


def test_add():
    """Add."""
    water = Molecule("Water", "H2O")
    inventory = ChemicalInventory()

    inventory.add(water, 12)

    assert inventory.get_quantity(water) == 12


def test_remove():
    """Remove."""
    water = Molecule("Water", "H2O")
    inventory = ChemicalInventory()

    inventory.add(water, 12)
    inventory.remove(water, 6)

    assert inventory.get_quantity(water) == 6


def test_negative_addition():
    """Negative addition."""
    water = Molecule("Water", "H2O")
    inventory = ChemicalInventory()

    inventory.add(water, 12)

    with pytest.raises(InvalidQuantityError):
        inventory.add(water, -6)


def test_negative_removal():
    """Negative removal."""
    water = Molecule("Water", "H2O")
    inventory = ChemicalInventory()

    inventory.add(water, 12)

    with pytest.raises(InvalidQuantityError):
        inventory.remove(water, -6)


def test_excessive_removal():
    """Excessive removal."""
    water = Molecule("Water", "H2O")
    inventory = ChemicalInventory()

    inventory.add(water, 12)

    with pytest.raises(InsufficientQuantityError):
        inventory.remove(water, 13)


def test_contains_negative_amount():
    """Contains negative amount."""
    water = Molecule("Water", "H2O")
    inventory = ChemicalInventory()

    inventory.add(water, 12)

    with pytest.raises(InvalidQuantityError):
        inventory.contains(water, -13)


def test_contains_excessive_amount():
    """Contains excessive amount."""
    water = Molecule("Water", "H2O")
    inventory = ChemicalInventory()

    inventory.add(water, 12)

    assert not inventory.contains(water, 13)


def test_excessive_removal_does_not_change_quantity():
    """Excessive removal does not change quantity."""
    water = Molecule("Water", "H2O")
    inventory = ChemicalInventory()
    inventory.add(water, 12)

    with pytest.raises(InsufficientQuantityError):
        inventory.remove(water, 13)

    assert inventory.get_quantity(water) == 12


def test_negative_removal_does_not_change_quantity():
    """Negative removal does not change quantity."""
    water = Molecule("Water", "H2O")
    inventory = ChemicalInventory()
    inventory.add(water, 12)

    with pytest.raises(InvalidQuantityError):
        inventory.remove(water, -6)

    assert inventory.get_quantity(water) == 12


def test_negative_addition_does_not_change_quantity():
    """Negative addition does not change quantity."""
    water = Molecule("Water", "H2O")
    inventory = ChemicalInventory()
    inventory.add(water, 12)

    with pytest.raises(InvalidQuantityError):
        inventory.add(water, -6)

    assert inventory.get_quantity(water) == 12


def test_returned_mapping_is_defensive_copy():
    """Returned mapping is defensive copy."""
    water = Molecule("Water", "H2O")
    salt = Molecule("Salt", "NaCl")

    inventory = ChemicalInventory()
    inventory.add(water, 10.0)

    returned_mapping = inventory.as_mapping

    returned_mapping[water] = 100.0
    returned_mapping[salt] = 5.0

    assert inventory.get_quantity(water) == 10.0
    assert inventory.get_quantity(salt) == 0.0


def test_quantity_close_to_zero_is_normalised():
    """Quantity close to zero is normalised."""
    water = Molecule("Water", "H2O")
    inventory = ChemicalInventory()

    inventory.add(water, 0.3)
    inventory.remove(water, 0.2)
    inventory.remove(water, 0.1)

    assert inventory.get_quantity(water) == 0.0


def test_quantity_above_zero_tolerance_is_preserved():
    """Quantity above zero tolerance is preserved."""
    water = Molecule("Water", "H2O")
    inventory = ChemicalInventory()

    inventory.add(water, 1e-8)

    assert inventory.get_quantity(water) == pytest.approx(1e-8)


@pytest.mark.parametrize(
    "invalid_amount", [float("nan"), float("inf"), float("-inf"), True, False]
)
def test_add_rejects_non_finite_values_and_booleans(invalid_amount):
    """Addition rejects non-finite numerical values and Boolean values."""
    water = Molecule("Water", "H2O")
    inventory = ChemicalInventory()

    with pytest.raises(InvalidQuantityError):
        inventory.add(water, invalid_amount)

    assert inventory.get_quantity(water) == 0.0


@pytest.mark.parametrize(
    "invalid_amount", [float("nan"), float("inf"), float("-inf"), True, False]
)
def test_remove_rejects_non_finite_values_and_booleans(invalid_amount):
    """Removal rejects non-finite numerical values and Boolean values."""
    water = Molecule("Water", "H2O")
    inventory = ChemicalInventory()
    inventory.add(water, 10.0)

    with pytest.raises(InvalidQuantityError):
        inventory.remove(water, invalid_amount)

    assert inventory.get_quantity(water) == 10.0


@pytest.mark.parametrize(
    "invalid_amount", [float("nan"), float("inf"), float("-inf"), True, False]
)
def test_contains_rejects_non_finite_values_and_booleans(invalid_amount):
    """Containment checks reject non-finite values and Boolean values."""
    water = Molecule("Water", "H2O")
    inventory = ChemicalInventory()

    with pytest.raises(InvalidQuantityError):
        inventory.contains(water, invalid_amount)
