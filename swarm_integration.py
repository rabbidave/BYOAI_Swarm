import threading
import time
import random
import logging
from queue import PriorityQueue
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Task:
    def __init__(self, task_id, description, priority=0, specialization=None):
        self.task_id = task_id
        self.description = description
        self.priority = priority
        self.specialization = specialization
        self.status = "pending"

    def __lt__(self, other):
        return self.priority > other.priority

class SwarmIntegration:
    def __init__(self):
        self.shared_context = PriorityQueue()
        self.lock = threading.Lock()
        self.agent_specializations = defaultdict(list)
        self.task_counter = 0
        self.active_agents = set()
        self.completed_tasks = []

    def add_task(self, description, priority=0, specialization=None):
        with self.lock:
            self.task_counter += 1
            task = Task(self.task_counter, description, priority, specialization)
            self.shared_context.put(task)
            logging.info(f"Added task: {task.description} (Priority: {task.priority}, Specialization: {task.specialization})")
        return task.task_id

    def get_task(self, agent_id):
        with self.lock:
            if not self.shared_context.empty():
                task = self.shared_context.get()
                if task.specialization is None or task.specialization in self.agent_specializations[agent_id]:
                    task.status = "in_progress"
                    return task
                else:
                    self.shared_context.put(task)
            return None

    def register_agent_specialization(self, agent_id, specializations):
        self.agent_specializations[agent_id] = specializations
        self.active_agents.add(agent_id)
        logging.info(f"Agent {agent_id} registered with specializations: {specializations}")

    def agent_worker(self, agent_id):
        while True:
            task = self.get_task(agent_id)
            if task:
                logging.info(f"Agent {agent_id} executing task {task.task_id}: {task.description}")
                # Simulate task execution
                time.sleep(random.uniform(0.5, 2.0))
                task.status = "completed"
                self.completed_tasks.append(task)
                logging.info(f"Agent {agent_id} completed task {task.task_id}")
            else:
                time.sleep(0.1)

    def start(self, num_agents=5):
        for i in range(num_agents):
            specializations = random.sample(["math", "language", "image", "audio"], k=random.randint(1, 3))
            self.register_agent_specialization(i, specializations)
            threading.Thread(target=self.agent_worker, args=(i,), daemon=True).start()

    def get_swarm_state(self):
        with self.lock:
            pending_tasks = list(self.shared_context.queue)
            return {
                "active_agents": len(self.active_agents),
                "pending_tasks": len(pending_tasks),
                "completed_tasks": len(self.completed_tasks),
                "agent_specializations": dict(self.agent_specializations)
            }

if __name__ == "__main__":
    swarm = SwarmIntegration()
    swarm.start()
    time.sleep(20)  # Let the simulation run for 20 seconds
