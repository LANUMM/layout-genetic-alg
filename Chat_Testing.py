import simpy


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


def container_monitor(env, container, threshold, pause_duration, replenish_amount):
    while True:
        # Wait for the trigger to check container level.
        yield container.monitor.trigger_check
        container.monitor.trigger_check = env.event()

        if container.level <= threshold:
            print(f'Container level dropped below threshold at {env.now}')
            yield env.timeout(pause_duration)
            yield container.put(replenish_amount)
            print(f'Replenished container at {env.now}')


env = simpy.Environment()
container = CustomContainer(env, capacity=100, init=50)

threshold = 10
pause_duration = 5
replenish_amount = 40

monitor = env.process(container_monitor(env, container, threshold, pause_duration, replenish_amount))
container.set_monitor(monitor)
monitor.trigger_check = env.event()

# Example of using the container
def example_usage(env, container):
    for _ in range(100):
        yield env.timeout(1)
        yield container.get(2)
        print(f'Got items from container at {env.now}')

env.process(example_usage(env, container))
env.run(until=50)