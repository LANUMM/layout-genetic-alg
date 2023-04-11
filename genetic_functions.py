import numpy as np
import pandas as pd

from helper_functions import get_weighted_from_to

# GLOBAL VARIABLES
weighted_from_to = get_weighted_from_to()


# Returns an array of pop_size number of totally randomized possible layouts
def generate_initial_population(pop_size: int):
    pop = []
    for i in range(pop_size):
        pop.append(generate_random_sample())

    return pop


# Test: 5x5 array, 5 1s, 5 2s, 5 3s, 5 4s, 5 5s
def generate_random_sample():
    machine_types = [1, 2, 3, 4, 5]

    # Create list of 5 of each machine type in random order
    machines = np.repeat(machine_types, repeats=5)
    np.random.shuffle(machines)

    # Reshape random list of machines into a 5x5 df 
    genome = pd.DataFrame(np.array(machines).reshape(5, 5))

    return genome


def score_pop_fitness(pop: list):
    # List of all scored_pops
    pop_scores = []
    for genome in pop:
        scored_genome = {
            "genome": genome,
            "score": score_genome_fitness(genome)
        }
        pop_scores.append(scored_genome)

    return pop_scores


def score_genome_fitness(genome):
    score = 0
    for row_idx in range(len(weighted_from_to.index)):
        for col_idx in range(len(weighted_from_to.columns)):
            if row_idx > 0:
                if col_idx < 6:
                    from_op = row_idx
                    to_op = col_idx
                    myVal = weighted_from_to.iloc[row_idx, col_idx]
                    a=1
    print(weighted_from_to)
    print(genome)
    return 9


my_pop = generate_initial_population(5)
scored_pop = score_pop_fitness(my_pop)