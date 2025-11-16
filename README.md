# qrng-hackaton_2025
Contains my project presented at the Qiskit Fall Fest PNC 2025 for the Quantum Random Number Generator hackaton.

## Project structure
qrng-hackathon_2025/
├── README.md
└── qrng/
    ├── circuit.py
    ├── runner.py
    └── Hackaton_2025_usage.ipynb
## Explanation
### circuit.py
Contains function build_qrng which generates a circuit creating a uniform superposition of all outcomes.

### runner.py
Contains function run_qrng. This function runs the circuit generated with build_qrng and return a random number.

The user can decide whether to use a real quantum backend or Aer local simulator.
Real backend is run with error mitigation/suppression techniques, whereas Aer includes a NoiseModel simulating the noise affecting a real backend.

The function returns a random integer number within the chosen range, together with different information on the output random distribution,
including its standard deviation to quantify its randomness (ideally, standard deviation = 0).

###  Hackaton_2025_usage.ipynb
Contains a usage example of run_qrng. The function is first run by using a real backend, than using AerSimulator. Finally, the uniformity of the two so-generated distributions
is compared by looking at their standard deviations.
