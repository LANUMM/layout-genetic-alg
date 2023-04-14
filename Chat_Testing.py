
def run_simulation_wrapper(run_number):
    return run_simulation(run_number + 1)

def evaluate_genome(genome):
    g.map = genome

    # Use a multiprocessing pool to run simulations in parallel
    with Pool() as pool:
        results = pool.map(run_simulation_wrapper, range(30))

    # Calculate the average objective function score
    average_objective_function_score = sum(results) / len(results)
    return average_objective_function_score

if __name__ == '__main__':
    genome = helper_functions.get_original_layout()
    results = []
    for x in range(30):
        results.append((evaluate_genome(genome)))
    print(results)