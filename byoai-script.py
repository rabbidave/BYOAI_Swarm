import os
import yaml
import logging
from swarm_integration import SwarmIntegration
from flask import Flask, request, jsonify, redirect
from werkzeug.exceptions import BadRequest, NotFound
import threading
import time

# Updated environment variables
CONTEXT_WORKFLOW_DIR = os.environ.get('CONTEXT_WORKFLOW_DIR', 'workflows')
CONTEXT_AGENT_PORT = int(os.environ.get('CONTEXT_AGENT_PORT', '8099'))
CONTEXT_AGENT_HOST = '0.0.0.0'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
swarm = SwarmIntegration()

def load_workflow(workflow_file):
    try:
        with open(os.path.join(CONTEXT_WORKFLOW_DIR, workflow_file), 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"Workflow file not found: {workflow_file}")
        return None
    except yaml.YAMLError as e:
        logging.error(f"Error parsing workflow file {workflow_file}: {str(e)}")
        return None

def execute_workflow(workflow):
    if not workflow:
        return
    for step in workflow['steps']:
        priority = step.get('priority', 5)
        specialization = step.get('specialization')
        task_id = swarm.add_task(step['name'], priority=priority, specialization=specialization)
        logging.info(f"Added task from workflow: {step['name']} (ID: {task_id})")

def monitor_and_scale_agents():
    while True:
        swarm_state = swarm.get_swarm_state()
        pending_tasks = swarm_state['pending_tasks']
        active_agents = swarm_state['active_agents']
        if pending_tasks > active_agents * 2:  # Scale up if there are more than 2 pending tasks per agent
            swarm.add_agent()
            logging.info(f"Scaled up: Added new agent. Total agents: {active_agents + 1}")
        time.sleep(10)  # Check every 10 seconds

@app.route('/')
def home():
    return "BYOAI agent is running"

@app.route('/status')
def status():
    return "BYOAI agent status: OK"

@app.route('/swarm/state')
def swarm_state():
    return jsonify(swarm.get_swarm_state())

@app.route('/swarm/add_task', methods=['GET', 'POST'])
def add_task():
    logging.info(f"Received {request.method} request to /swarm/add_task")
    
    if request.method == 'GET':
        return jsonify({
            "message": "To add a task, send a POST request to this endpoint with a JSON payload containing 'description' (required), 'priority' (optional), 'specialization' (optional), and 'timeout' (optional)",
            "example": {
                "description": "Example task",
                "priority": 5,
                "specialization": "math",
                "timeout": 30
            }
        }), 200

    elif request.method == 'POST':
        if not request.is_json:
            raise BadRequest("Content-Type must be application/json")

        data = request.get_json()

        if not data:
            raise BadRequest("Empty JSON payload")

        if 'description' not in data:
            raise BadRequest("Task description is required")

        task_id = swarm.add_task(
            description=data['description'],
            priority=data.get('priority', 5),
            specialization=data.get('specialization'),
            timeout=data.get('timeout', 30)
        )
        return jsonify({"task_id": task_id, "message": "Task added successfully"}), 201

@app.route('/swarm/task_status/<int:task_id>')
def task_status(task_id):
    status = swarm.get_task_status(task_id)
    if status:
        return jsonify(status), 200
    raise NotFound("Task not found")

@app.route('/swarm/remove_completed_tasks', methods=['POST'])
def remove_completed_tasks():
    max_completed = request.json.get('max_completed', 100)
    swarm.remove_completed_tasks(max_completed)
    return jsonify({"message": f"Removed completed tasks, keeping the last {max_completed}"}), 200

@app.route('/swarm/agent_load')
def agent_load():
    return jsonify(swarm.get_swarm_state()['agent_load']), 200

@app.route('/swarm/redistribute_tasks', methods=['POST'])
def redistribute_tasks():
    threshold = request.json.get('threshold', 5)
    swarm.redistribute_tasks(threshold)
    return jsonify({"message": f"Redistributed tasks with threshold {threshold}"}), 200

@app.route('/swarm/statistics')
def swarm_statistics():
    return jsonify(swarm.get_swarm_statistics()), 200

@app.route('/agents/scale', methods=['POST'])
def scale_agents():
    data = request.get_json()
    num_agents = data.get('num_agents', 1)
    for _ in range(num_agents):
        swarm.add_agent()
    return jsonify({"message": f"Added {num_agents} agents"})

@app.route('/http:/localhost:8099/<path:subpath>')
def handle_misformed_url(subpath):
    """
    Handle misformed URLs that include 'http://localhost:8099/' in the path.
    Redirect to the correct endpoint.
    """
    return redirect('/' + subpath)

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({"error": str(e)}), 400

@app.errorhandler(NotFound)
def handle_not_found(e):
    return jsonify({"error": str(e)}), 404

@app.errorhandler(Exception)
def handle_generic_error(e):
    logging.error(f"Unexpected error: {str(e)}")
    return jsonify({"error": "An unexpected error occurred"}), 500

def main():
    logging.info(f"BYOAI agent running on {CONTEXT_AGENT_HOST}:{CONTEXT_AGENT_PORT}")
    logging.info(f"Loading workflows from {CONTEXT_WORKFLOW_DIR}")
    
    swarm.start(num_agents=5)

    # Start the agent monitoring and scaling thread
    threading.Thread(target=monitor_and_scale_agents, daemon=True).start()

    # Load and execute workflows
    for workflow_file in os.listdir(CONTEXT_WORKFLOW_DIR):
        if workflow_file.endswith('.yml'):
            workflow = load_workflow(workflow_file)
            if workflow:
                logging.info(f"Executing workflow: {workflow['name']}")
                execute_workflow(workflow)
            else:
                logging.error(f"Failed to load workflow: {workflow_file}")

    # Start Flask app
    app.run(host=CONTEXT_AGENT_HOST, port=CONTEXT_AGENT_PORT, debug=True)

if __name__ == "__main__":
    main()