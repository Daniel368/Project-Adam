##### Purpose



Diffusion provides passive molecule movement between well-mixed compartments.





##### Model



flux = permeability × area × (source concentration - destination concentration)



requested transfer = flux × delta\_time



where:

* permeability controls how easily the molecule moves;
* area represents the contact area;
* concentration is quantity divided by volume;
* delta\_time is the duration of one simulation step.





##### Direction



Diffusion must automatically move material from higher concentration to lower concentration.



The caller must not manually specify the direction.





##### Constraints



* compartments are internally well mixed;
* only one molecule is handled by each diffusion process;
* diffusion is deterministic;
* permeability and area remain constant;
* equilibrium is approached but must not be overshot;
* diffusion cannot create or destroy quantity;
* no active transport is modelled;
* no electrical charge is modelled;
* no membrane proteins are modelled.





##### Open questions



* How will membranes control permeability?
* Should permeability depend on molecule properties?
* How will electrical gradients affect ions?
* Should diffusion become spatial later?
* How should stochastic movement be represented?
* Should temperature affect diffusion rates?

