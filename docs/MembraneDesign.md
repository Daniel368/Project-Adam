##### Purpose



A membrane separates two compartments and controls passive movement according to molecule-specific permeability





##### Model



Membrane

├── inside compartment

├── outside compartment

├── surface area

└── permeability table

&#x20;       Molecule → permeability





##### Assumptions



* both compartments are internally well mixed;
* membrane area is constant;
* permeability is constant during a simulation step;
* unregistered molecules cannot cross;
* transport remains passive;
* movement always follows the concentration gradient;
* the membrane does not consume energy;
* the membrane does not model thickness yet;
* there are no channels, pumps or carrier proteins yet;
* electrical charge does not affect movement yet.





##### Responsibilities



The membrane is responsible for:



* storing its two adjacent compartments;
* storing membrane area;
* storing molecule-specific permeability;
* permitting or blocking passive transport;
* advancing all configured passive transport processes.



It is not responsible for:



* chemical reactions;
* active transport;
* cellular metabolism;
* deciding what a cell needs;
* producing or destroying molecules.





##### Open questions



* Should membrane thickness be represented?
* How should ion channels be modelled?
* How will voltage affect ion transport?
* How should carrier saturation be represented?
* Should permeability change dynamically?
* How will membrane damage be represented?
* How should membrane growth and division work?





