"""Tests for chemical compartments and molecule transfers."""

import pytest

from adam.chemistry.compartment import Compartment
from adam.chemistry.molecule import Molecule
from adam.chemistry.exceptions import (
    ChemistryError,
    InvalidQuantityError,
    InvalidVolumeError,
    InsufficientQuantityError,
)


def test_positive_volume_works():
    """Positive volume is accepted."""
    compartment = Compartment("Cytoplasm", 10.0)

    assert compartment.volume == 10.0


def test_zero_volume_fails():
    """Zero volume raises the expected error."""
    with pytest.raises(InvalidVolumeError):
        Compartment("Cytoplasm", 0.0)


def test_negative_volume_fails():
    """Negative volume raises the expected error."""
    with pytest.raises(InvalidVolumeError):
        Compartment("Cytoplasm", -10.0)


def test_concentration_is_calculated_correctly():
    """Concentration is calculated correctly."""
    water = Molecule("Water", "H2O")
    compartment = Compartment("Cytoplasm", 4.0)

    compartment.add(water, 12.0)

    assert compartment.get_concentration(water) == pytest.approx(3.0)


def test_missing_molecule_has_zero_concentration():
    """Missing molecule has zero concentration."""
    water = Molecule("Water", "H2O")
    compartment = Compartment("Cytoplasm", 4.0)

    assert compartment.get_concentration(water) == 0.0


def test_transfer_modifies_both_compartments_correctly():
    """Transfer modifies both compartments correctly."""
    water = Molecule("Water", "H2O")

    source = Compartment("Source", 10.0)
    destination = Compartment("Destination", 10.0)

    source.add(water, 12.0)

    source.transfer_to(destination, water, 5.0)

    assert source.get_quantity(water) == pytest.approx(7.0)
    assert destination.get_quantity(water) == pytest.approx(5.0)


def test_transfer_adds_to_existing_destination_quantity():
    """Transfer adds to existing destination quantity."""
    water = Molecule("Water", "H2O")

    source = Compartment("Source", 10.0)
    destination = Compartment("Destination", 10.0)

    source.add(water, 12.0)
    destination.add(water, 3.0)

    source.transfer_to(destination, water, 5.0)

    assert source.get_quantity(water) == pytest.approx(7.0)
    assert destination.get_quantity(water) == pytest.approx(8.0)


def test_insufficient_transfer_leaves_both_compartments_unchanged():
    """Insufficient transfer leaves both compartments unchanged."""
    water = Molecule("Water", "H2O")

    source = Compartment("Source", 10.0)
    destination = Compartment("Destination", 10.0)

    source.add(water, 4.0)
    destination.add(water, 2.0)

    with pytest.raises(InsufficientQuantityError):
        source.transfer_to(destination, water, 5.0)

    assert source.get_quantity(water) == pytest.approx(4.0)
    assert destination.get_quantity(water) == pytest.approx(2.0)


def test_negative_transfer_fails():
    """Negative transfer raises the expected error."""
    water = Molecule("Water", "H2O")

    source = Compartment("Source", 10.0)
    destination = Compartment("Destination", 10.0)

    source.add(water, 10.0)

    with pytest.raises(InvalidQuantityError):
        source.transfer_to(destination, water, -2.0)


def test_negative_transfer_leaves_both_compartments_unchanged():
    """Negative transfer leaves both compartments unchanged."""
    water = Molecule("Water", "H2O")

    source = Compartment("Source", 10.0)
    destination = Compartment("Destination", 10.0)

    source.add(water, 10.0)
    destination.add(water, 3.0)

    with pytest.raises(InvalidQuantityError):
        source.transfer_to(destination, water, -2.0)

    assert source.get_quantity(water) == pytest.approx(10.0)
    assert destination.get_quantity(water) == pytest.approx(3.0)


def test_same_compartment_transfer_fails():
    """Same compartment transfer raises the expected error."""
    water = Molecule("Water", "H2O")
    compartment = Compartment("Cytoplasm", 10.0)

    compartment.add(water, 10.0)

    with pytest.raises(ChemistryError):
        compartment.transfer_to(compartment, water, 3.0)


def test_same_compartment_transfer_leaves_quantity_unchanged():
    """Same compartment transfer leaves quantity unchanged."""
    water = Molecule("Water", "H2O")
    compartment = Compartment("Cytoplasm", 10.0)

    compartment.add(water, 10.0)

    with pytest.raises(ChemistryError):
        compartment.transfer_to(compartment, water, 3.0)

    assert compartment.get_quantity(water) == pytest.approx(10.0)


@pytest.mark.parametrize("invalid_volume", [float("nan"), float("inf"), float("-inf"), True, False])
def test_volume_rejects_non_finite_values_and_booleans(invalid_volume):
    """Compartment volume rejects non-finite values and Boolean values."""
    with pytest.raises(InvalidVolumeError):
        Compartment("Cytoplasm", invalid_volume)


@pytest.mark.parametrize("invalid_amount", [float("nan"), float("inf"), float("-inf"), True, False])
def test_transfer_rejects_non_finite_values_and_booleans(invalid_amount):
    """Transfers reject non-finite numerical values and Boolean values."""
    water = Molecule("Water", "H2O")
    source = Compartment("Source", 10.0)
    destination = Compartment("Destination", 10.0)
    source.add(water, 10.0)

    with pytest.raises(InvalidQuantityError):
        source.transfer_to(destination, water, invalid_amount)

    assert source.get_quantity(water) == 10.0
    assert destination.get_quantity(water) == 0.0
