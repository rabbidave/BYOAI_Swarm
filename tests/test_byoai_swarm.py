import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
import time
import threading

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from swarm_integration import SwarmIntegration, Task
from byoai_script import app

class TestBYOAISwarmIntegration(unittest.TestCase):

    def setUp(self):
        self.swarm = SwarmIntegration()
        self.app = app.test_client()

    def test_add_task(self):
        task_id = self.swarm.add_task("Test Task", priority=3, specialization="math")
        self.assertIsInstance(task_id, int)
        self.assertIn(task_id, self.swarm.task_map)

    def test_get_task(self):
        self.swarm.add_task("Test Task", priority=3, specialization="math")
        self.swarm.register_agent(0, ["math"])
        task = self.swarm.get_task(0)
        self.assertIsInstance(task, Task)
        self.assertEqual(task.description, "Test Task")

    def test_register_agent(self):
        self.swarm.register_agent(1, ["language", "math"])
        self.assertIn(1, self.swarm.swarm.agents)
        self.assertEqual(self.swarm.swarm.agents[1], ["language", "math"])

    def test_api_add_task(self):
        response = self.app.post('/swarm/add_task', json={
            'description': 'API Test Task',
            'priority': 5,
            'specialization': 'math'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('task_id', response.json)

    def test_get_swarm_state(self):
        self.swarm.add_task("Test Task 1", priority=3, specialization="math")
        self.swarm.add_task("Test Task 2", priority=2, specialization="language")
        state = self.swarm.get_swarm_state()
        self.assertIn('active_agents', state)
        self.assertIn('pending_tasks', state)
        self.assertEqual(state['pending_tasks'], 2)

    def test_task_priority(self):
        self.swarm.add_task("Low Priority Task", priority=1)
        self.swarm.add_task("High Priority Task", priority=10)
        self.swarm.register_agent(0, [])
        task = self.swarm.get_task(0)
        self.assertIsNotNone(task)
        self.assertEqual(task.description, "High Priority Task")

    def test_agent_specialization_matching(self):
        self.swarm.register_agent(0, ["math"])
        self.swarm.register_agent(1, ["language"])
        
        math_task_id = self.swarm.add_task("Math Task", specialization="math")
        language_task_id = self.swarm.add_task("Language Task", specialization="language")
        
        math_task = self.swarm.get_task(0)
        language_task = self.swarm.get_task(1)
        
        self.assertIsNotNone(math_task)
        self.assertIsNotNone(language_task)
        self.assertEqual(math_task.task_id, math_task_id)
        self.assertEqual(language_task.task_id, language_task_id)

    def test_task_timeout(self):
        task_id = self.swarm.add_task("Timeout Task", timeout=1)
        time.sleep(2)  # Wait for the task to timeout
        
        task_status = self.swarm.get_task_status(task_id)
        self.assertIsNotNone(task_status)
        self.assertEqual(task_status['status'], 'pending')  # Assuming 'pending' is the initial status

    def test_agent_failure_simulation(self):
        self.swarm.register_agent(0, ["math"])
        task_id = self.swarm.add_task("Failure Test Task", specialization="math")
        
        # Simulate agent failure
        del self.swarm.swarm.agents[0]
        
        # Task should be reassigned
        self.swarm.register_agent(1, ["math"])
        reassigned_task = self.swarm.get_task(1)
        
        self.assertIsNotNone(reassigned_task)
        self.assertEqual(reassigned_task.task_id, task_id)

    def test_performance_under_load(self):
        start_time = time.time()
        num_tasks = 1000
        
        for i in range(num_tasks):
            self.swarm.add_task(f"Performance Test Task {i}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.assertLess(total_time, 2, f"Adding {num_tasks} tasks took too long: {total_time:.2f} seconds")

if __name__ == '__main__':
    unittest.main()
