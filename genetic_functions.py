import numpy as np
import pandas as pd
import random

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

# Returns a score for a genome
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
    return score

#
def keep_top_n(n, scored_pop):
    # sort the list of dictionaries by ascending score
    sorted_scored_pop = sorted(scored_pop, key=lambda x: x['score'])
    # return the first n dictionaries from the sorted list
    return sorted_scored_pop[:n]

def choose_parents(scored_pop):
    # calculate the inverse of each score (to prioritize lower scores)
    inverse_scores = [1 / x['score'] for x in scored_pop]
    # calculate the sum of the inverse scores
    sum_inverse_scores = sum(inverse_scores)
    # normalize the inverse scores
    norm_inverse_scores = [x / sum_inverse_scores for x in inverse_scores]
    # use the normalized inverse scores as probabilities for random choice
    indices = random.choices(range(len(scored_pop)), weights=norm_inverse_scores, k=2)
    # return the two dictionaries at the chosen indices
    return [scored_pop[i] for i in indices]

# TODO: track down bug where its not returning valid genome
def crossover(parents):
    parent1 = parents[0]["genome"]
    parent2 = parents[1]["genome"]

    child = pd.DataFrame(np.zeros((5, 5)))

    options = [1, 2, 3, 4, 5]
    counts = [5, 5, 5, 5, 5]

    positions = [(i, j) for i in range(5) for j in range(5)]
    np.random.shuffle(positions)
    for i, j in positions:
        if child.loc[i, j] == 0:
            if np.random.random() < 0.5:
                value = parent1.loc[i, j]
                other_parent = parent2
            else:
                value = parent2.loc[i, j]
                other_parent = parent1

            if counts[value - 1] > 0:
                child.loc[i, j] = value
                counts[value - 1] -= 1
            else:
                if value in options:
                    options.remove(value)

                # Try the other parent
                other_value = other_parent.loc[i, j]
                if counts[other_value - 1] > 0:
                    child.loc[i, j] = other_value
                    counts[other_value - 1] -= 1
                else:
                    if other_value in options:
                        options.remove(other_value)

                    # If neither parent works, choose randomly
                    random_value = np.random.choice(options)
                    child.loc[i, j] = random_value
                    counts[random_value - 1] -= 1

    if check_valid(child):
        return child
    else:
        return crossover(parents)


# Get the rectilinear distance between one operation and another (also works for from starting and to ending)
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

def check_valid(df):
    count_1 = (df == 1).sum().sum()
    count_2 = (df == 2).sum().sum()
    count_3 = (df == 3).sum().sum()
    count_4 = (df == 4).sum().sum()
    count_5 = (df == 5).sum().sum()
    if count_1 == 5 and count_2 == 5 and count_3 == 5 and count_4 == 5 and count_5 == 5:
        return True
    else:
        return False


my_pop = generate_initial_population(5)
scored_pop = score_pop_fitness(my_pop)
parents = choose_parents(scored_pop)
kiddo = crossover(parents)
print(check_valid(kiddo))
a = 1
#a_genome = generate_random_sample()
#yeet = _get_mean_distance(a_genome, 1, 2)