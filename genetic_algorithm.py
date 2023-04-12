from genetic_functions import *

# HYPER PARAMS
population_size = 10
top_n_to_keep = 2
mutations_per_genome = 1
iterations = 100

# ALGORITHM
initial_pop = generate_initial_population(population_size)
pop = initial_pop
for i in range(iterations):
    scored_pop = score_pop_fitness(pop)
    log_population_info(scored_pop, i)
    next_gen = keep_top_n(n=top_n_to_keep, scored_pop=scored_pop)
    while len(next_gen) < population_size:
        parents = choose_parents(scored_pop)
        child_genome = crossover(parents)
        mutated_genome = mutation(child_genome, mutations_per_genome)
        next_gen.append(mutated_genome)
    pop = next_gen

#PRINT FINAL LAYOUT
