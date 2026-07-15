"""Demonstrate glucose oxidation using Adam's public chemistry API."""

from adam.chemistry import Compartment, Molecule, Reaction


def main() -> None:
    """Create and execute one unit of the glucose oxidation reaction."""
    glucose = Molecule("Glucose", "C6H12O6")
    oxygen = Molecule("Oxygen", "O2")
    carbon_dioxide = Molecule("Carbon dioxide", "CO2")
    water = Molecule("Water", "H2O")

    glucose_oxidation = Reaction(
        name="Glucose oxidation",
        reactants={glucose: 1.0, oxygen: 6.0},
        products={carbon_dioxide: 6.0, water: 6.0},
    )

    cell = Compartment("Cell", volume=1.0)
    cell.add(glucose, 1.0)
    cell.add(oxygen, 6.0)

    print("Before reaction:")
    for molecule in (glucose, oxygen, carbon_dioxide, water):
        print(f"  {molecule.name}: {cell.get_quantity(molecule)}")

    glucose_oxidation.execute(cell, extent=1.0)

    print("After reaction:")
    for molecule in (glucose, oxygen, carbon_dioxide, water):
        print(f"  {molecule.name}: {cell.get_quantity(molecule)}")


if __name__ == "__main__":
    main()
