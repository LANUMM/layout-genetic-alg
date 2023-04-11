import numpy as np


# Returns an array of pop_size number of totally randomized possible layouts
def generate_initial_population(pop_size: int):
    pop = []
    for i in range(pop_size):
        pop.append(generate_random_sample())

    return pop


# Test: 5x5 array, 5 1s, 5 2s, 5 3s, 5 4s, 5 5s
def generate_random_sample():
    # Create an empty 5x5 array
    genome = np.zeros((5, 5), dtype=int)

    machine_types = [1, 2, 3, 4, 5]

    # Create list of all possible machine coordinates
    machine_coordinates = [(i, j) for i in range(5) for j in range(5)]

    # Create list of 5 of each machine type in random order
    machines = np.repeat(machine_types, repeats=5)
    np.random.shuffle(machines)

    # Fill 5x5 array with machines
    for i, coordinate in enumerate(machine_coordinates):
        genome[coordinate] = machines[i]

    return genome


