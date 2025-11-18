from qiskit.visualization import plot_histogram
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# For transpiling
from qiskit.transpiler import generate_preset_pass_manager

# For real backends
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import SamplerV2 as Sampler

# For simulator backend
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, amplitude_damping_error    # To simulate amplitude damping error if simulator is chosen

# Import function for generating qrng circuit
from circuit import build_qrng


def run_qrng(num_outcomes: int, shots: int = 1, simulator: bool = True, show_circuit: bool = False, show_histo = False) -> (int, float):
    """
    Run the Quantum Random Number Generator circuit, using either a real backed or a local simulator.

    Args:
        num_outcomes (int): Number of possible random outcomes (n).
        shots (int): Number of times to run the circuit.
        simulator (bool): Choose whether to use a real backend (False) or a local simulator (True). Real one requires log in
        show_circuit (bool): If True, show the transpiled circuit. Useful for real backends
        show_histo (bool): If True, show histogram of the measurement results

    Returns:
        int: A random number between 0 and num_outcomes-1
        float: normalized standard deviation of the measured distribution
    """
    # Build the circuit using build_qrng function
    qc, num_qubits = build_qrng(num_outcomes)
    
    # Choose the backend: a real one or a local simulator
    # For real backends, noise naturally affects computation: no noise model needed
    service = QiskitRuntimeService()
    if simulator == False:
        print("Chosen backend: real\n")
        
        # Setup the backend
        backend = service.least_busy(operational = True, simulator = False, min_num_qubits = num_qubits)
        
        # Setup primitive and set it as runner
        runner = Sampler(mode = backend)
        
        # Set simple error suppression/mitigation options
        runner.options.dynamical_decoupling.enable = True
        runner.options.dynamical_decoupling.sequence_type = "XY4"
        runner.options.twirling.enable_gates = True
        runner.options.twirling.num_randomizations = "auto"
        
        print(f"Backend: {backend}\n")
        print("Error suppression/mitigation techniques implemented: dynamical decoupling and gate twirling\n")
        
    else:
        print("Chosen backend: local simulator\n")

        # Setup a simulated noise. Here we simulate the noise one would encounter when using a real backend
        noise_backend = service.least_busy(operational = True, simulator = False, min_num_qubits = num_qubits)
        noise_model = NoiseModel.from_backend(noise_backend)

        # Setup the backend and set it as runner
        backend = AerSimulator(noise_model = noise_model)
        runner = backend
        
        print(f"Simulator: {backend}\n")
        print(f"Simulated noise: {noise_backend}\n")
    
    # Transpile the circuit
    pm = generate_preset_pass_manager(backend = backend, optimization_level = 2)
    transpiled_qc = pm.run(qc)
    if show_circuit:
        print("Transpiled circuit for the chosen backend:\n")
        display(transpiled_qc.decompose(reps = 2).draw(output = "mpl", fold = -1, idle_wires = False))
    
    # Create job and run it
    job = runner.run([(transpiled_qc)], shots = shots)
    if simulator == False:
        result = job.result()[0]
        counts_binary = result.data.c.get_counts()
    else:
        result = job.result()
        counts_binary = result.get_counts()
    
    # Plot results
    if show_histo:
        print(f"Distribution of the {shots} outcomes:\n")
        histo = plot_histogram(counts_binary, figsize = (14,6))
        display(histo)
    
    # Convert measured outcomes into integers
    counts_int = {int(bitstring, 2): occurrence for bitstring, occurrence in counts_binary.items()}
    outcomes = list(counts_int.keys())
    print(f"Outcomes: {sorted(outcomes)}\n")
    
    # Compute normalized standard deviation of the outcomes
    occurrences = list(counts_int.values())
    std_norm = round(np.std(occurrences)/np.mean(occurrences), 9)  # Normalized standard deviation, rounded
    std_norm = float(std_norm)
    print(f"Normalized standard deviation: {std_norm:.3g}\n")
    
    # Filters results whose (integer) outcomes are in the user's desired range
    valid_counts = {outcome: occurrence for outcome, occurrence in counts_int.items() if outcome < num_outcomes}
    valid_outcomes = list(valid_counts.keys())
    print(f"Desired range: [0, {num_outcomes-1}]")
    print(f"Valid outcomes: {sorted(valid_outcomes)}\n")
    
    # Probe the (integer) outcome which occurred more frequently. Since each shot provides quantum randomness, this value is random too
    valid_occurrences = list(valid_counts.values())
    max_occurrence = max(valid_occurrences)
    max_indices = [index for index, occ in enumerate(valid_occurrences) if occ == max_occurrence]   
    
    # If there are multiple outcomes with maximum frequency, re-run the circuit with a single shot. Else, extract the most frequent outcome
    if len(max_indices) > 1:
        print("Multiple outcomes with maximum frequency: re-run the circuit with shots = 1\n")
        single_job = runner.run([(transpiled_qc)], shots = 1)
        if simulator == False:
            result = single_job.result()[0]
            count = result.data.c.get_counts()
        else:
            result = single_job.result()
            count = result.get_counts()
            
        random_num = list(count.keys())[0]
        random_num = int(random_num, 2)
    else:
        # Otherwise, extract the outcome which occurred more frequently
        random_num = valid_outcomes[max_indices[0]]
    
    return random_num, std_norm