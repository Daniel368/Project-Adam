from adam.biology import Membrane
from adam.chemistry import Compartment, Molecule

glucose = Molecule("Glucose", "C6H12O6")
oxygen = Molecule("Oxygen", "O2")
sodium = Molecule("Sodium", "Na+")

inside = Compartment("Inside", volume=1.0)
inside.add(glucose, 0.0)
inside.add(oxygen, 0.0)
inside.add(sodium, 10.0)

outside = Compartment("Outside", volume=3.0)
outside.add(glucose, 12.0)
outside.add(oxygen, 12.0)
outside.add(sodium, 0.0)

membrane = Membrane(
    inside=inside,
    outside=outside,
    area=1.0,
)

membrane.set_permeability(glucose, 0.1)
membrane.set_permeability(oxygen, 0.8)
membrane.set_permeability(sodium, 0.0)

delta_time = 0.1

for tick in range(21):
    time = tick * delta_time

    print(
        f"tick={tick:2d} "
        f"time={time:4.1f} "
        f"inside_O2={inside.get_concentration(oxygen):7.4f} "
        f"outside_O2={outside.get_concentration(oxygen):7.4f} "
        f"inside_glucose={inside.get_concentration(glucose):7.4f} "
        f"outside_glucose={outside.get_concentration(glucose):7.4f} "
        f"inside_Na={inside.get_concentration(sodium):7.4f} "
        f"outside_Na={outside.get_concentration(sodium):7.4f}"
    )

    if tick < 20:
        membrane.step(delta_time)
