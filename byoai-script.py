import os
import yaml
import logging
from swarm_integration import SwarmIntegration
from flask import Flask, request, jsonify

# Updated environment variables
CONTEXT_WORKFLOW_DIR = os.environ.get('CONTEXT_WORKFLOW_DIR', 'workflows')
CONTEXT_AGENT_PORT = int(os.environ.get('CONTEXT_AGENT_PORT', '8000'))
CONTEXT_AGENT_HOST = os.environ.get('CONTEXT_AGENT_HOST', '0.0.0.0')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
swarm = SwarmIntegration()

def load_workflow(workflow_file):
    with open(os.path.join(CONTEXT_WORKFLOW_DIR, workflow_file), 'r') as f:
        return yaml.safe_load(f)

def execute_workflow(workflow):
    for step in workflow['steps']:
        priority = step.get('priority', 5)
        specialization = step.get('specialization')
        swarm.add_task(step['name'], priority=priority, specialization=specialization)

@app.route('/')
def home():
    return "BYOAI agent is running"

@app.route('/status')
def status():
    return "BYOAI agent status: OK"

@app.route('/swarm/state')
def swarm_state():
    return jsonify(swarm.get_swarm_state())

@app.route('/swarm/add_task', methods=['POST'])
def add_task():
    data = request.json
    task_id = swarm.add_task(
        description=data['description'],
        priority=data.get('priority', 5),
        specialization=data.get('specialization')
    )
    return jsonify({"task_id": task_id, "message": "Task added successfully"})

def main():
    logging.info(f"BYOAI agent running on {CONTEXT_AGENT_HOST}:{CONTEXT_AGENT_PORT}")
    logging.info(f"Loading workflows from {CONTEXT_WORKFLOW_DIR}")
    
    swarm.start(num_agents=5)

    # Load and execute workflows
    for workflow_file in os.listdir(CONTEXT_WORKFLOW_DIR):
        if workflow_file.endswith('.yml'):
            workflow = load_workflow(workflow_file)
            logging.info(f"Executing workflow: {workflow['name']}")
            execute_workflow(workflow)

    # Start Flask app
    app.run(host=CONTEXT_AGENT_HOST, port=CONTEXT_AGENT_PORT)

if __name__ == "__main__":
    main()
