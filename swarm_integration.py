import threading
import time
import random

class SwarmIntegration:
    def __init__(self):
        self.shared_context = []
        self.lock = threading.Lock()

    def add_task(self, task):
        with self.lock:
            self.shared_context.append(task)

    def get_task(self):
        with self.lock:
            if self.shared_context:
                return self.shared_context.pop(0)
            return None

    def agent_worker(self, agent_id):
        while True:
            task = self.get_task()
            if task:
                print(f"Agent {agent_id} executing task: {task}")
                # Simulate task execution
                time.sleep(random.uniform(0.5, 2.0))
            else:
                time.sleep(0.1)

    def start(self, num_agents=5):
        for i in range(num_agents):
            threading.Thread(target=self.agent_worker, args=(i,), daemon=True).start()

        # Simulate adding tasks to the shared context
        for i in range(20):
            self.add_task(f"Task {i}")
            time.sleep(random.uniform(0.1, 0.5))

if __name__ == "__main__":
    swarm = SwarmIntegration()
    swarm.start()
    time.sleep(10)  # Let the simulation run for 10 seconds
