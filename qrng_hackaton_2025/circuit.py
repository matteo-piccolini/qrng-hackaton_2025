from qiskit import QuantumCircuit
import math

def build_qrng(num_outcomes: int) -> (QuantumCircuit, int):
    """
    Build a Quantum Random Number Generator circuit.

    Args:
        num_outcomes (int): Number of possible random outcomes (n).

    Returns:
        QuantumCircuit: A circuit that prepares a superposition state.
        int: Number of qubits used.
    """
    # Find number of qubits num_qubits required to represent num_outcomes
    num_qubits = math.ceil(math.log2(num_outcomes))
    print(f"Number of qubits required: {num_qubits}\n")
    
    # Create a quantum circuit with num_qubits qubits and the same amount of classical bits
    qc = QuantumCircuit(num_qubits, num_qubits)
    
    # Apply Hadamard gates to all qubits to create a uniform superposition of 2**num_qubits states
    for q in range(num_qubits):
        qc.h(q)
    
    # Measure all qubits
    qc.measure(range(num_qubits), range(num_qubits))
    
    return qc, num_qubits

