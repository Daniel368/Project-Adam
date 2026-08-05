"""Custom exception hierarchy for the biology package."""


class BiologyError(Exception):
    """Base class for all biology-system errors."""


class InvalidMembraneError(BiologyError):
    """Raised when the membrane construction or area is invalid"""


class MoleculeTransportError(BiologyError):
    """Raised when the permeability related operations are invalid"""
