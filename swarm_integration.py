import threading
import time
import random
import logging
from queue import PriorityQueue
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Task:
    def __init__(self, task_id, description, priority=0, specialization=None, timeout=30):
        self.task_id = task_id
        self.description = description
        self.priority = priority
        self.specialization = specialization
        self.status = "pending"
        self.start_time = None
        self.completion_time = None
        self.assigned_agent = None
        self.timeout = timeout

    def __lt__(self, other):
        return self.priority > other.priority

class Swarm:
    def __init__(self):
        self.tasks = PriorityQueue()
        self.agents = {}

    def add_task(self, task):
        self.tasks.put(task)

    def get_task(self, agent_id, specializations):
        for _ in range(self.tasks.qsize()):
            task = self.tasks.get()
            if task.specialization is None or task.specialization in specializations:
                task.assigned_agent = agent_id
                task.status = "in_progress"
                task.start_time = time.time()
                return task
            self.tasks.put(task)
        return None

    def complete_task(self, task, agent_id):
        task.status = "completed"
        task.completion_time = time.time()

    def register_agent(self, agent_id, specializations):
        self.agents[agent_id] = specializations

    def pending_tasks_count(self):
        return self.tasks.qsize()

    def get_agent_tasks(self, agent_id):
        return [task for task in self.tasks.queue if task.assigned_agent == agent_id]

    def reassign_task(self, task):
        task.assigned_agent = None
        task.status = "pending"
        self.tasks.put(task)

class SwarmIntegration:
    def __init__(self):
        self.swarm = Swarm()
        self.lock = threading.Lock()
        self.agent_specializations = defaultdict(list)
        self.task_counter = 0
        self.active_agents = set()
        self.completed_tasks = []
        self.task_map = {}
        self.agent_load = defaultdict(int)
        self.agent_performance = defaultdict(lambda: {"completed": 0, "total_time": 0})
        self.start_time = time.time()
        self.agent_counter = 0

    def add_task(self, description, priority=0, specialization=None, timeout=30):
        with self.lock:
            self.task_counter += 1
            task = Task(self.task_counter, description, priority, specialization, timeout)
            self.swarm.add_task(task)
            self.task_map[task.task_id] = task
            logging.info(f"Added task: {task.description} (Priority: {task.priority}, Specialization: {task.specialization})")
        return task.task_id

    def get_task(self, agent_id):
        with self.lock:
            task = self.swarm.get_task(agent_id, self.agent_specializations[agent_id])
            if task:
                self.agent_load[agent_id] += 1
            return task

    def register_agent_specialization(self, agent_id, specializations):
        self.agent_specializations[agent_id] = specializations
        self.active_agents.add(agent_id)
        self.swarm.register_agent(agent_id, specializations)
        logging.info(f"Agent {agent_id} registered with specializations: {specializations}")

    def agent_worker(self, agent_id):
        while True:
            task = self.get_task(agent_id)
            if task:
                logging.info(f"Agent {agent_id} executing task {task.task_id}: {task.description}")
                # Simulate task execution
                execution_time = random.uniform(0.5, 2.0)
                time.sleep(execution_time)
                
                self.swarm.complete_task(task, agent_id)
                
                with self.lock:
                    self.completed_tasks.append(task)
                    self.agent_load[agent_id] -= 1
                    self.agent_performance[agent_id]["completed"] += 1
                    self.agent_performance[agent_id]["total_time"] += execution_time
                
                logging.info(f"Agent {agent_id} completed task {task.task_id}")
            else:
                time.sleep(0.1)

    def start(self, num_agents=5):
        for _ in range(num_agents):
            self.add_agent()

    def add_agent(self):
        with self.lock:
            agent_id = self.agent_counter
            self.agent_counter += 1
            specializations = random.sample(["math", "language", "image", "audio"], k=random.randint(1, 3))
            self.register_agent_specialization(agent_id, specializations)
            threading.Thread(target=self.agent_worker, args=(agent_id,), daemon=True).start()
            logging.info(f"Added new agent {agent_id} with specializations: {specializations}")
        return agent_id

    def get_swarm_state(self):
        with self.lock:
            return {
                "active_agents": len(self.active_agents),
                "pending_tasks": self.swarm.pending_tasks_count(),
                "completed_tasks": len(self.completed_tasks),
                "agent_specializations": dict(self.agent_specializations),
                "agent_load": dict(self.agent_load),
                "agent_performance": self._calculate_agent_performance()
            }

    def get_task_status(self, task_id):
        task = self.task_map.get(task_id)
        if task:
            return {
                "task_id": task.task_id,
                "status": task.status,
                "description": task.description,
                "priority": task.priority,
                "specialization": task.specialization,
                "assigned_agent": task.assigned_agent,
                "start_time": task.start_time,
                "completion_time": task.completion_time
            }
        return None

    def remove_completed_tasks(self, max_completed=100):
        with self.lock:
            if len(self.completed_tasks) > max_completed:
                removed_tasks = self.completed_tasks[:-max_completed]
                self.completed_tasks = self.completed_tasks[-max_completed:]
                for task in removed_tasks:
                    del self.task_map[task.task_id]
                logging.info(f"Removed {len(removed_tasks)} completed tasks from history")

    def redistribute_tasks(self, threshold=5):
        with self.lock:
            overloaded_agents = [agent_id for agent_id, load in self.agent_load.items() if load > threshold]
            for agent_id in overloaded_agents:
                tasks_to_redistribute = self.swarm.get_agent_tasks(agent_id)
                for task in tasks_to_redistribute:
                    self.swarm.reassign_task(task)
                self.agent_load[agent_id] -= len(tasks_to_redistribute)
                logging.info(f"Redistributed {len(tasks_to_redistribute)} tasks from overloaded agent {agent_id}")

    def get_swarm_statistics(self):
        with self.lock:
            total_tasks = len(self.completed_tasks) + self.swarm.pending_tasks_count()
            avg_completion_time = sum((task.completion_time - task.start_time for task in self.completed_tasks if task.completion_time)) / len(self.completed_tasks) if self.completed_tasks else 0
            return {
                "total_tasks_processed": total_tasks,
                "average_completion_time": avg_completion_time,
                "tasks_per_specialization": self._count_tasks_per_specialization(),
                "agent_efficiency": self._calculate_agent_efficiency(),
                "swarm_uptime": time.time() - self.start_time
            }

    def _count_tasks_per_specialization(self):
        specialization_count = defaultdict(int)
        for task in self.completed_tasks + list(self.task_map.values()):
            specialization_count[task.specialization] += 1
        return dict(specialization_count)

    def _calculate_agent_efficiency(self):
        return {agent_id: perf["completed"] / perf["total_time"] if perf["total_time"] > 0 else 0
                for agent_id, perf in self.agent_performance.items()}

    def _calculate_agent_performance(self):
        return {agent_id: {
            "completed_tasks": perf["completed"],
            "average_task_time": perf["total_time"] / perf["completed"] if perf["completed"] > 0 else 0,
            "efficiency": perf["completed"] / perf["total_time"] if perf["total_time"] > 0 else 0
        } for agent_id, perf in self.agent_performance.items()}

if __name__ == "__main__":
    swarm_integration = SwarmIntegration()
    swarm_integration.start()
    time.sleep(20)  # Let the simulation run for 20 seconds
