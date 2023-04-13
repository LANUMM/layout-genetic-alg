import helper_functions
from helper_functions import get_operations

import simpy
import random
import pandas as pd
import csv

# Class to store global parameter values
class g:
    order_arrival_rate = 4 # the interval that orders arrive (expo dist)
    types = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] # possible types of orders
    type_prob = [0.1, 0.2, 0.05, 0.1, 0.2, 0.05, 0.1, 0.10, 0.05, 0.05] # the probability of each kind of order
    operations = helper_functions.get_operations() # returns a dataframe of with rows for each kind of job and columns for the required operations
    p_time = helper_functions.get_ptime() # dataframe of the processing time of each operation for each type of job
    edge = 2 # the distance between each layout coordinate
    setup_time = 10 # If a machine needs to be set up, it takes this time
    reorder_point = 100 # If the number of raws drops below this value, it puts in an order of quantity reorder_quantity and it takes leadtime time
    reorder_quantity = 200 #
    raws = 200 # the initial quantity of raw materials available. Should be made into a container. Each order takes only one raw material
    leadtime = 500 # the time it takes from placing an order for raw materials to geting the raw materials
    map = helper_functions.get_original_layout() # a 5x5 dataframe holding the layout (with 5 1s, 5 2s and so on for each machine type (operation type)


# Class representing the orders coming into the factory
class Job:
    def __init__(self, job_type, operation_sequence):
        self.job_type = job_type
        self.operation_sequence = operation_sequence


# Class representing a machine. It's a simpy.Resource with custom attributes
class Machine(simpy.Resource):
    def __init__(self, env, machine_type, location):
        super().__init__(env, capacity=1)
        self.machine_type = machine_type
        self.location = location


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


class Factory_Model:
    def __int__(self, run_number):
        self.env = simpy.Environment()
        self.order_counter = 0
        self.run_number = run_number

        # Create machines
        self.machines = create_machines_from_map(self.env, g.map)

        # Create raw parts storage and end-product storage
        self.raw_parts_storage = simpy.Container(self.env, capacity=float('inf'), init=g.raws)
        self.end_product_storage = simpy.Container(self.env, capacity=float('inf'), init=0)

    def process_job(self, job):
        for operation in job.operation_sequence:
            # Find available machine for the current operation
            machine = self.find_available_machine(operation)

            # Check for raw parts availability and wait if necessary
            yield self.raw_parts_storage.get(1)

            # Check for machine setup time and wait if necessary
            yield self.env.timeout(g.setup_time)

            # Process the part on the machine
            with machine.request() as req:
                yield req
                yield self.env.timeout(g.p_time.loc[job.job_type, operation])

            # Transport the part to the next machine or end-product storage
            yield self.env.process(self.transport(operation, self.end_product_storage, g.edge))


    def job_generator(self, job_arrival_distribution, setup_time, transport_time):
        while True:
            job_type = random.choices(g.types, weights=g.type_prob, k=1)[0]
            operation_sequence = g.operations.loc[job_type-1].tolist()
            job = Job(job_type, operation_sequence=operation_sequence)
            self.env.process(self.process_job(job))
            yield self.env.timeout(random.expovariate(g.order_arrival_rate))




self.env.process(self.process_job(job, setup_time, transport_time))
