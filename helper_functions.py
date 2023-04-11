import pandas as pd


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
