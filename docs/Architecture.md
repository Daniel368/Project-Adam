Environment
│
├── Chemistry
│     ├── Molecules
│     ├── Reactions
│     ├── Diffusion
│     └── Temperature
│
├── Cell
│     ├── Membrane
│     ├── DNA
│     ├── ATP
│     └── Metabolism
│
├── Tissue
│     ├── Cell Communication
│     ├── Adhesion
│     └── Differentiation
│
├── Nervous System
│     ├── Neuron (inherits Cell)
│     ├── Synapse
│     └── Glia
│
└── Brain
      ├── Cortex
      ├── Hippocampus
      ├── Thalamus
      └── ...


There are many modules that will be used in the project Adam, many will contain various sub-modules. The major ones include but not limited to:

-Environment: This module will include many physics and chemistry concepts, it is the study of how environment works relevant to evolution, it will be completely independent of all the other modules and will be used as a foundation to build all the other modules are.

-Chemistry: Without Chemistry, there would be no Biology, in order to many interactions that happen within a cell and in between the cell and other cells or the environment, one must have comprehensive knowledge of certain molecules and their characteristics

-Cell: This is self explanatory, in order to write code on cells, we need to know about cells, more specifically, the study of cells, or Cell Biology.

-Genetics: once we are done with simulating how cells behave, the most important milestone is simulating how genes work, after all, genes are the thing that determines how the cell or more precisely, how the whole organism does and has many things, it acts as a blueprint.

-Tissue: Another milestone would be simulate tissues, where we have many cells, cooperating with each other to form a tissue.

-Nervous System: In order to understand how brain works, we need to first figure out nervous system as it directly connects to the brain and is responsible for many functions in humans.

-Brain: Finally, the Brain which is at the centre, everything so far comes together to create a better picture of how brain works.



Here's a dependency diagram:

Environment
   ↓
Chemistry
   ↓
Cells
   ↓
Tissues
   ↓
Nervous System 
   ↓
Brain
 

Here's is a diagram of different layers of project Adam:

Application Layer
│
├── Simulation Engine
│
Biological Systems
│
├── Brain
├── Nervous System
├── Tissue
├── Cell
├── Genetics
├── Chemistry
│
Infrastructure
│
├── Environment
├── Utilities
├── Configuration
├── Logging
