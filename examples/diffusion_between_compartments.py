from adam.chemistry.compartment import Compartment
from adam.chemistry.diffusion import PassiveDiffusion
from adam.chemistry.molecule import Molecule
from adam.simulation.engine import SimulationEngine


def print_state(
    engine: SimulationEngine,
    glucose: Molecule,
    compartment_a: Compartment,
    compartment_b: Compartment,
) -> None:
    quantity_a = compartment_a.get_quantity(glucose)
    quantity_b = compartment_b.get_quantity(glucose)

    print(
        f"tick={engine.clock.tick:3d} "
        f"time={engine.clock.time:5.2f} "
        f"qA={quantity_a:7.4f} "
        f"qB={quantity_b:7.4f} "
        f"cA={compartment_a.get_concentration(glucose):7.4f} "
        f"cB={compartment_b.get_concentration(glucose):7.4f} "
        f"total={quantity_a + quantity_b:7.4f}"
    )


def main() -> None:
    glucose = Molecule(name="Glucose", symbol="C6H12O6")

    compartment_a = Compartment(name="A", volume=1.0)
    compartment_b = Compartment(name="B", volume=3.0)

    compartment_a.add(glucose, 10.0)

    diffusion = PassiveDiffusion(
        molecule=glucose,
        compartment_a=compartment_a,
        compartment_b=compartment_b,
        permeability=0.2,
        area=1.0,
    )

    engine = SimulationEngine()
    engine.add_process(diffusion)

    print("Expected equilibrium: concentration=2.5, qA=2.5, qB=7.5")
    print_state(engine, glucose, compartment_a, compartment_b)

    for _ in range(20):
        engine.step(0.1)
        print_state(engine, glucose, compartment_a, compartment_b)


if __name__ == "__main__":
    main()
