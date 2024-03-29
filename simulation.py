import helper_functions
from helper_functions import get_operations

import simpy
import random
from multiprocessing import Pool
import gevent
import pandas as pd
import csv
import heapq


# Class to store global parameter values
class g:
    order_arrival_rate = 4 # the AVERAGE interval that orders arrive
    types = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] # possible types of orders
    type_prob = [0.1, 0.2, 0.05, 0.1, 0.2, 0.05, 0.1, 0.10, 0.05, 0.05] # the probability of each kind of order
    operations = helper_functions.get_operations().reset_index(drop=True) # returns a dataframe of with rows for each kind of job and columns for the required operations
    p_time = helper_functions.get_ptime().reset_index(drop=True) # dataframe of the processing time of each operation for each type of job
    edge = 2 # the distance between each layout coordinate
    setup_time = 10 # If a machine needs to be set up, it takes this time
    reorder_point = 128 # If the number of raws drops below this value, it puts in an order of quantity reorder_quantity and it takes leadtime time
    reorder_quantity = 128 #
    raws = 200 # the initial quantity of raw materials available.
    leadtime = 500 # the time it takes from placing an order for raw materials to geting the raw materials
    map = helper_functions.get_original_layout() # a 5x5 dataframe holding the layout (with 5 1s, 5 2s and so on for each machine type (operation type)


# Class representing the orders coming into the factory
class Job:
    def __init__(self, job_type, operation_sequence, starting_location, arrival_time):
        self.job_type = job_type
        self.operation_sequence = operation_sequence
        self.operation_position = 0
        self.location = starting_location
        self.arrival_time = arrival_time
        self.delays = []
        self.travel_time = 0

    def __lt__(self, other):
        return self.arrival_time < other.arrival_time

# Class representing a machine. It's a simpy.Resource with custom attributes
class Machine(simpy.Resource):
    def __init__(self, env, machine_type, location):
        super().__init__(env, capacity=1)
        self.machine_type = machine_type
        self.location = location
        self.queue = []
        self.setup_for = None

# Takes a pandas df as machine_map basically as a genome
def create_machines_from_map(env, machine_map):
    machines = []
    for row in range(machine_map.shape[0]):
        for col in range(machine_map.shape[1]):
            machine_type = machine_map.iloc[row, col]
            location = (row + 1, col + 1)
            machine = Machine(env, machine_type, location)
            machines.append(machine)
    return machines

class CustomContainer(simpy.Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitor = None

    def get(self, amount):
        if self.monitor is not None and not self.monitor.trigger_check.triggered:
            self.monitor.trigger_check.succeed()
        return super().get(amount)

    def set_monitor(self, monitor):
        self.monitor = monitor


def container_monitor(env, container, rng):
    while True:
        # Wait for the trigger to check container level.
        yield container.monitor.trigger_check
        container.monitor.trigger_check = env.event()

        if container.level <= g.reorder_point:
            #print(f'Container level dropped below threshold at {env.now}')
            chosen_leadtime = rng.uniform(g.leadtime - g.leadtime * 0.1, g.leadtime + g.leadtime * 0.1)
            yield env.timeout(chosen_leadtime)
            yield container.put(g.reorder_quantity)
            #print(f'Replenished container at {env.now}')


class FactoryModel:
    def __init__(self, run_number, layout_map):
        # Set random seed based on run number
        self.rng = random.Random(run_number)

        # Metrics
        self.waiting_times = []
        self.parts_in_system = []
        self.parts_processed = 0
        self.total_travel_time = 0

        self.env = simpy.Environment()
        self.order_counter = 0
        self.run_number = run_number
        self.stop_event = self.env.event()

        # Create machines
        self.machines = create_machines_from_map(self.env, layout_map)

        # Create raw parts storage
        self.raw_parts_storage = CustomContainer(self.env, capacity=float('inf'), init=g.raws)
        self.monitor = self.env.process(
            container_monitor(self.env, self.raw_parts_storage, self.rng))
        self.raw_parts_storage.set_monitor(self.monitor)
        self.monitor.trigger_check = self.env.event()
        self.raw_parts_location = (3, 0)  # Raw materials starting location

        # Create end-product storage
        self.end_product_storage = simpy.Container(self.env, capacity=float('inf'), init=0)
        self.end_product_location = (3, 6)  # End product storage location

    def process_job(self, job):
        # If job is new get raw material
        if job.operation_position == 0:
            yield self.raw_parts_storage.get(1)
            # Find available machine for the current operation - find machine with shortest queue
            machine = self.find_shortest_queue_machine(job.operation_sequence[0])

            # Travel to machine
            yield self.env.process(self.transport(job, machine, g.edge))


        # Capture average jobs in system
        # Record the number of parts in the system at this time
        parts_in_system = sum(
            [len(m.queue) for m in self.machines]) + self.raw_parts_storage.level
        self.parts_in_system.append(parts_in_system)

        for operation in job.operation_sequence:
            # Find available machine for the current operation - find machine with shortest queue
            machine = self.find_shortest_queue_machine(operation)

            # Travel to machine
            yield self.env.process(self.transport(job, machine, g.edge))

            # Add the part to the queue of the chosen machine - Add the job to the machine's queue
            part_arrival_time = self.env.now
            machine.queue.append((part_arrival_time, job))
            machine.queue.sort(key=lambda x: x[0])  # Sort the queue based on arrival time

            start_que_wait = self.env.now
            # Process the part on the machine
            with machine.request() as req:
                yield req
                que_wait = self.env.now - start_que_wait
                job.delays.append({"name": "queue", "duration": que_wait})
                machine.queue.pop(0)  # Remove the job from the queue when it starts processing
                # Check if the machine is set up for the current job type
                if machine.setup_for != job.job_type:
                    # If not, delay by setup time and set up the machine for the current job type
                    yield self.env.timeout(g.setup_time)
                    machine.setup_for = job.job_type

                m_processing_time = g.p_time.iloc[job.operation_position, job.job_type - 1]
                job.delays.append({"name": "machining", "duration": m_processing_time})
                yield self.env.timeout(m_processing_time)

            # Update the job's operation_position
            job.operation_position += 1
            job.location = machine.location

        # Finished last required operation j
        # Travel from last machine to end point
        yield self.env.process(self.transport(job, self.end_product_storage, g.edge))

        # Add job to final parts storage
        self.end_product_storage.put(1)
        self.parts_processed += 1

        # If parts processed is 1000 end the sim
        if self.parts_processed >= 1000:
            self.stop_event.succeed()

        # Record the waiting time for the job
        waiting_time = self.env.now - job.arrival_time
        self.waiting_times.append(waiting_time)

        # Record the number of parts in the system at this time
        parts_in_system = sum(
            [len(m.queue) for m in self.machines]) + self.raw_parts_storage.level
        self.parts_in_system.append(parts_in_system)

        # Record total travel time
        self.total_travel_time += job.travel_time

    def calculate_stats(self):
        average_waiting_time = sum(self.waiting_times) / len(self.waiting_times)
        average_parts_in_system = sum(self.parts_in_system) / len(self.parts_in_system)
        return average_waiting_time, average_parts_in_system
        # return self.total_travel_time

    def job_generator(self):
        while True:
            job_type = self.rng.choices(g.types, weights=g.type_prob, k=1)[0]
            operation_sequence = g.operations.loc[job_type-1].tolist()  # TODO: validate this works
            operation_sequence = [x for x in operation_sequence if x != 0]  # Trim operation sequence to get rid of 0s
            job = Job(job_type, operation_sequence=operation_sequence, starting_location=self.raw_parts_location
                      , arrival_time=self.env.now)
            self.env.process(self.process_job(job))
            yield self.env.timeout(self.rng.expovariate(1/g.order_arrival_rate))

    def transport(self, job, destination, edge):
        if destination == self.end_product_storage:
            destination_location = self.end_product_location
        else:
            destination_location = destination.location

        if job.location is not None:
            rectilinear_distance = abs(job.location[0] - destination_location[0]) + abs(
                job.location[1] - destination_location[1])
        else:
            rectilinear_distance = 0  # Assume no travel time for the first operation

        travel_time = rectilinear_distance * edge  # Calculate travel time based on rectilinear distance
        job.delays.append({"name": "transport", "duration": travel_time})
        job.travel_time += travel_time
        yield self.env.timeout(travel_time)  # Wait for travel_time to elapse

    def get_machines_for_operation(self, operation):
        selected_machines = [machine for machine in self.machines if machine.machine_type == operation]
        return selected_machines

    def find_shortest_queue_machine(self, operation):
        # Get the machines for the current operation
        machines = self.get_machines_for_operation(operation)

        # Find the machine with the shortest queue
        shortest_queue = min(machines, key=lambda machine: len(machine.queue))

        return shortest_queue


def run_simulation(run_number, genome):
    model = FactoryModel(run_number, genome)
    model.env.process(model.job_generator())
    model.env.run(until=model.stop_event)  # Set an appropriate simulation time
    avg_waiting_time, avg_parts_in_system = model.calculate_stats()
    #total_travel_time = model.calculate_stats()
    #print("Avg Waiting Time: {:<5}".format(avg_waiting_time))
    #print("Avg Parts In System: {:<5}".format(avg_parts_in_system))
    objective_function = 2 * avg_waiting_time + avg_parts_in_system
    #print("TOTAL SCORE: {:<5}".format(objective_function))
    return objective_function


def run_simulation_wrapper(args):
    run_number, genome = args
    return run_simulation(run_number + 1, genome)


def evaluate_genome(genome):
    # Create a list of tuples (run_number, genome) to be used as arguments
    args_list = [(i, genome) for i in range(10)]

    # Use a multiprocessing pool to run simulations in parallel
    with Pool() as pool:
        results = pool.map(run_simulation_wrapper, args_list)

    # Calculate the average objective function score
    average_objective_function_score = sum(results) / len(results)
    return average_objective_function_score

#if __name__ == '__main__':
#    genome = helper_functions.get_original_layout()
#    results = []
#    results.append((evaluate_genome(genome)))
#    for x in range(3):
 #       results.append((evaluate_genome(genome)))
 #   print(results)