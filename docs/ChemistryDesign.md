##### 1\. Purpose



Chemistry provides the necessary means for all the cellular functions. Without Chemistry, the would me no food, no replication, transcription, transformation, transportation, movement, etc... Chemistry provides the ability for cells to survive and thrive in the environment. Lastly, the Chemistry module is completely independent of every other module in this project.





##### 2\. Core concepts





* Molecule: A group of two or more atoms held together by chemical bonds, acting as the smallest fundamental unit of a chemical compound that can take part in a chemical reaction.
* Quantity: The measurable amount of a substance, typically expressed in physical units like mass (grams) or chemical units like moles to represent the number of particles.
* Inventory: An accounting of all the materials, atoms, or molecules present in the system, detailing what is coming in, what is leaving, and what remains inside.
* Compartment: A defined, isolated, or distinct physical or conceptual space in which a reaction or process takes place, often used to model separate phases or spatial regions in a system.
* Reaction: A process in which one or more substances are transformed into different substances, involving the breaking and forming of chemical bonds.
* Reactant: A starting material in a chemical reaction that is consumed as the process takes place.
* Product: A substance formed as a result of a chemical reaction.
* Stoichiometric coefficient: The number placed in front of a chemical formula in a balanced equation to indicate the exact proportions of molecules or moles of each substance taking part in the reaction.
* Reaction extent: A thermodynamic variable representing how far a chemical reaction has progressed; it translates the change in the amount of any given substance into a standardized scale corresponding to the overall progress of the reaction





##### 3\. Units





Quantity: arbitrary simulation units

Volume: arbitrary simulation volume units

Concentration: quantity / volume

Time: simulation ticks





##### 4\. Assumptions





* Molecules are immutable definitions.
* Quantities cannot be negative.
* Compartments are internally well mixed.
* Reactions occur instantaneously when explicitly executed.
* Reactions do not run automatically.
* Temperature and pressure do not affect reactions yet.
* Reaction rates are not modelled yet.
* Matter is conserved according to the declared reaction equation.





##### 5\. Dependencies





The chemistry package may depend on:



* Python standard library;
* shared utility code, if genuinely required.



It must not depend on:



* cell;
* genetics;
* tissue;
* nervous system;
* brain.



##### 

##### 6\. Open questions





* When should arbitrary units be replaced by physical units?
* Should future reactions use deterministic or stochastic kinetics?
* How will spatial diffusion be represented?
* Should molecules later include charge and molecular mass?
* How will enzymes modify reaction rates?
* Should gravity be represented?
* When should temperature and pressure be taken into account?

