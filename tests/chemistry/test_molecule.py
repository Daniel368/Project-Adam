"""Tests for immutable molecule value objects."""

from dataclasses import FrozenInstanceError

import pytest

from adam.chemistry.exceptions import InvalidNameError
from adam.chemistry.molecule import Molecule


def test_name_is_stored():
    """Name is stored."""
    molecule = Molecule("Water", "H2O")

    assert molecule.name == "Water"


def test_symbol_is_stored():
    """Symbol is stored."""
    molecule = Molecule("Water", "H2O")

    assert molecule.symbol == "H2O"


def test_empty_name_raises():
    """Empty name raises."""
    with pytest.raises(InvalidNameError):
        Molecule("", "H2O")


def test_empty_symbol_raises():
    """Empty symbol raises."""
    with pytest.raises(InvalidNameError):
        Molecule("Water", "")


def test_equality():
    """Equality."""
    molecule1 = Molecule("Water", "H2O")
    molecule2 = Molecule("Water", "H2O")

    assert molecule1 == molecule2


def test_molecule_is_hashable():
    """Molecule is hashable."""
    molecule = Molecule("Water", "H2O")

    assert isinstance(hash(molecule), int)


def test_molecule_can_be_dict_key():
    """Molecule can be dict key."""
    molecule = Molecule("Water", "H2O")

    data = {molecule: "liquid"}

    assert data[molecule] == "liquid"


def test_equal_molecules_are_one_set_element():
    """Equal molecules are one set element."""
    molecule1 = Molecule("Water", "H2O")
    molecule2 = Molecule("Water", "H2O")

    molecules = {molecule1, molecule2}

    assert len(molecules) == 1


def test_name_cannot_be_changed():
    """Name cannot be changed."""
    molecule = Molecule("Water", "H2O")

    with pytest.raises(FrozenInstanceError):
        molecule.name = "Salt"


def test_symbol_cannot_be_changed():
    """Symbol cannot be changed."""
    molecule = Molecule("Water", "H2O")

    with pytest.raises(FrozenInstanceError):
        molecule.symbol = "NaCl"
