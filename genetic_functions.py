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
            from_op = row_idx
            to_op = col_idx
            # Cant go to start or from end
            if (to_op != 0) & (from_op != 6):
                # From Start to End causes problems
                if not (from_op == 0) & (to_op == 6):
                    weight = weighted_from_to.iloc[row_idx, col_idx]
                    distance = _get_mean_distance(genome, op_from=from_op, op_to=to_op)
                    score += weight * distance
                    a = weighted_from_to
    return score

def _get_mean_distance(genome, op_from: int, op_to: int):
    # From Start (raw material) to an operation
    if op_from == 0:
        # Realative coordinates of material starting location
        from_avg_row = 2 # effectivly node 3
        from_avg_col = -1

        # Get mean coordinates of to operation machines
        to_mask = genome == op_to
        to_coordinates = to_mask.stack()[to_mask.stack()].index.tolist()
        to_avg_row = sum([coord[0] for coord in to_coordinates]) / len(to_coordinates)
        to_avg_col = sum([coord[1] for coord in to_coordinates]) / len(to_coordinates)

    # From an operation to End (final product location)
    elif op_to == 6:
        # Realative coordinates of final product location
        to_avg_row = 2
        to_avg_col = 5

        # Get mean coordinates of from operation machines
        from_mask = genome == op_from
        from_coordinates = from_mask.stack()[from_mask.stack()].index.tolist()
        from_avg_row = sum([coord[0] for coord in from_coordinates]) / len(from_coordinates)
        from_avg_col = sum([coord[1] for coord in from_coordinates]) / len(from_coordinates)

    #From an operation to another operation
    else:
        # Get mean coordinates of from operation machines
        from_mask = genome == op_from
        from_coordinates = from_mask.stack()[from_mask.stack()].index.tolist()
        from_avg_row = sum([coord[0] for coord in from_coordinates]) / len(from_coordinates)
        from_avg_col = sum([coord[1] for coord in from_coordinates]) / len(from_coordinates)

        # Get mean coordinates of to operation machines
        to_mask = genome == op_to
        to_coordinates = to_mask.stack()[to_mask.stack()].index.tolist()
        to_avg_row = sum([coord[0] for coord in to_coordinates]) / len(to_coordinates)
        to_avg_col = sum([coord[1] for coord in to_coordinates]) / len(to_coordinates)

    # Get rectilinear distance between the means
    dist = abs(from_avg_row - to_avg_row) + abs(from_avg_col - to_avg_col)

    return dist

my_pop = generate_initial_population(5)
scored_pop = score_pop_fitness(my_pop)
a = 1
#a_genome = generate_random_sample()
#yeet = _get_mean_distance(a_genome, 1, 2)