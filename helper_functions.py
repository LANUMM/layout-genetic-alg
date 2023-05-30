import pandas as pd
import numpy as np


# Generate weighted scoring from-to-chart
def get_weighted_from_to():
    # Read csv of order of operations each kind of job needs to go through
    operations_order = pd.read_csv('operation_order.csv')
    operations_order = operations_order.set_index('Job_Type')

    # Read csv of the probability of each kind of job
    type_prob = pd.read_csv('type_prob.csv')
    type_prob = type_prob.set_index('Type')

    # Create weighted from-to-chart with 0s init
    names = ['Start', 'Op1', 'Op2', 'Op3', 'Op4', 'Op5', 'End']
    weighted_from_to = pd.DataFrame(0, index=names, columns=names)

    # For each kind of job
    for job in range(10):
        # Get the operations that job goes through
        operations = operations_order.iloc[job]
        # Get the probability of that job occuring
        prob = type_prob.iloc[job]
        # For each operation for that job
        for i in range(5):
            # If it's the first operation account for material leaving starting position and going to first operation
            if i == 0:
                weighted_from_to.iloc[0, operations[i]] += prob
            if (i < 4) & (operations[i] != 0):
                if operations[i+1] != 0:
                    weighted_from_to.iloc[operations[i], operations[i+1]] += prob
                # If there are less than 5 operations, account for material going from last operation to exit
                if operations[i+1] == 0:
                    weighted_from_to.iloc[operations[i], 6] += prob
            # If there are 5 operations account for material going from last operation to exit
            if (i == 4) & (operations[i] != 0):
                weighted_from_to.iloc[operations[i], 6] += prob

    return weighted_from_to

def get_original_layout():
    df = pd.read_csv('final_map.csv', header=None)
    lst = df[0].values.tolist()
    ordered_cords = [(lst[i], lst[i+1]) for i in range(0, len(lst), 2)]
    ordered_cords_shift = [(lst[i]-1, lst[i+1]-1) for i in range(0, len(lst), 2)][:25]
    coords = ordered_cords_shift
    genome = pd.DataFrame(data=0, index=range(5), columns=range(5))
    for i in range(1, 6):
        indices = [coord for coord in coords if genome.loc[coord[0], coord[1]] == 0][:5]
        if len(indices) < 5:
            raise ValueError(f"Not enough coordinates for value {i}")
        for coord in indices:
            genome.loc[coord[0], coord[1]] = i
    return genome


def genome_to_arena(genome):
    lst = []
    for i in range(1, 6):
        coords = [(r+1, c+1) for r, c in zip(*np.where(genome.values == i))]
        lst.extend(coords)
    expanded_lst = [item for tpl in lst for item in tpl]
    expanded_lst.extend([0, 3, 6, 3])

    return expanded_lst


def get_operations():
    # Read csv of order of operations each kind of job needs to go through
    operations_order = pd.read_csv('operation_order.csv')
    operations_order = operations_order.set_index('Job_Type')
    return operations_order


def get_ptime():
    # Read csv of processing time for each operation for each type of job
    ptime = pd.read_csv('ptime.csv', index_col=0)
    return ptime

get_original_layout()