import unittest
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from byoai-script import load_workflow, execute_workflow
from swarm_integration import SwarmIntegration

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Set up test environment variables
        os.environ['CONTEXT_WORKFLOW_DIR'] = 'test_workflows'
        os.environ['CONTEXT_AGENT_PORT'] = '8000'
        os.environ['CONTEXT_AGENT_HOST'] = '0.0.0.0'

    def test_load_workflow(self):
        # Create a test workflow file
        os.makedirs('test_workflows', exist_ok=True)
        with open('test_workflows/test_workflow.yml', 'w') as f:
            f.write("name: Test Workflow\nsteps:\n  - name: Step 1\n    action: test_action")

        workflow = load_workflow('test_workflow.yml')
        self.assertEqual(workflow['name'], 'Test Workflow')
        self.assertEqual(len(workflow['steps']), 1)

    def test_swarm_integration(self):
        swarm = SwarmIntegration()
        swarm.add_task("Test Task")
        task = swarm.get_task()
        self.assertEqual(task, "Test Task")

    def tearDown(self):
        # Clean up test files
        import shutil
        shutil.rmtree('test_workflows', ignore_errors=True)

if __name__ == '__main__':
    unittest.main()
