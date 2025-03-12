import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, Aer, execute
from qiskit.visualization import plot_state_qsphere, plot_bloch_multivector, plot_histogram

# Function to create a simple quantum circuit
def create_circuit():
    circuit = QuantumCircuit(2)
    circuit.h(0)  # Apply Hadamard gate to qubit 0
    circuit.cx(0, 1)  # Apply CNOT gate to qubit 1
    return circuit

# Function to simulate the quantum circuit
def simulate_circuit(circuit):
    # Use Aer's qasm_simulator
    simulator = Aer.get_backend('statevector_simulator')
    
    # Execute circuit on simulator
    result = execute(circuit, backend=simulator).result()
    
    # Get the state vector
    statevector = result.get_statevector()
    return statevector

# Function to visualize quantum states on Q-sphere
def visualize_qsphere(statevector):
    plot_state_qsphere(statevector)
    plt.title("Quantum State Q-sphere")
    plt.show()

# Function to visualize qubit states on Bloch sphere
def visualize_bloch(statevector):
    # Extracting individual qubit states
    state_0 = statevector[0]
    state_1 = statevector[1]

    # Prepare Bloch vectors
    bloch_vector_0 = [2 * np.real(state_0), 2 * np.imag(state_0), np.abs(state_0) ** 2]
    bloch_vector_1 = [2 * np.real(state_1), 2 * np.imag(state_1), np.abs(state_1) ** 2]

    # Visualizing Bloch sphere
    fig, axes = plt.subplots(1, 2, subplot_kw=dict(projection='3d'))
    axes[0].set_title("Qubit 0")
    axes[1].set_title("Qubit 1")

    for ax, bloch_vector in zip(axes, [bloch_vector_0, bloch_vector_1]):
        ax.quiver(0, 0, 0, bloch_vector[0], bloch_vector[1], bloch_vector[2],
                  color='r', arrow_length_ratio=0.1)
        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        ax.set_zlabel('Z-axis')

    plt.show()

# Function to implement Grover's Algorithm
def grovers_algorithm(num_qubits=2):
    circuit = QuantumCircuit(num_qubits)

    # Initialize the qubits
    circuit.h(range(num_qubits))

    # Apply the oracle - flipping the target amplitude
    circuit.z(1)
    circuit.cz(0, 1)

    # Apply the Grover diffusion operator
    circuit.h(range(num_qubits))
    circuit.x(range(num_qubits))
    circuit.h(num_qubits - 1)
    circuit.cx(0, 1)
    circuit.h(num_qubits - 1)
    circuit.x(range(num_qubits))
    circuit.h(range(num_qubits))

    return circuit

# Function to perform Grover's search simulation
def simulate_grovers():
    circuit = grovers_algorithm()
    statevector = simulate_circuit(circuit)
    return statevector

# Function to analyze the output of a quantum measurement
def analyze_output(statevector):
    counts = np.abs(statevector) ** 2
    return counts

# Main function to run the simulations
def main():
    print("Running simple quantum circuit simulation...")
    circuit = create_circuit()
    statevector = simulate_circuit(circuit)
    print(f"Statevector: {statevector}")

    visualize_qsphere(statevector)
    visualize_bloch(statevector)

    print("Running Grover's algorithm simulation...")
    grover_statevector = simulate_grovers()
    print(f"Grover's Statevector: {grover_statevector}")

    output_counts = analyze_output(grover_statevector)
    print(f"Output counts: {output_counts}")

    plt.bar(range(len(output_counts)), output_counts)
    plt.title("Output Probability Distribution")
    plt.xlabel("State")
    plt.ylabel("Probability")
    plt.xticks(range(len(output_counts)), [f"|{i}> " for i in range(len(output_counts))])
    plt.show()

if __name__ == "__main__":
    main()