# BYOAI with Swarm Integration

## Introduction

This project integrates the BYOAI (Bring Your Own AI) framework with OpenAI's Swarm, creating a powerful, decentralized, and context-driven agent system. The integration provides a flexible and scalable solution for distributed task execution and AI-driven workflows.

## Features

- Decentralized agent architecture
- Context-driven task distribution
- Specialization-based task assignment
- Priority queue for efficient task management
- RESTful API for task submission and status monitoring
- Dynamic agent scaling based on workload
- Detailed logging and monitoring
- Task redistribution for load balancing

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-repo/byoai-swarm.git
   cd byoai-swarm
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   export CONTEXT_WORKFLOW_DIR=workflows
   export CONTEXT_AGENT_PORT=8099
   export CONTEXT_AGENT_HOST=0.0.0.0
   ```

## Usage

1. Start the BYOAI-Swarm system:
   ```
   python byoai-script.py
   ```

2. Access the API endpoints:
   - Home: `http://localhost:8099/`
   - Status: `http://localhost:8099/status`
   - Swarm State: `http://localhost:8099/swarm/state`
   - Add Task: `POST http://localhost:8099/swarm/add_task`
   - Task Status: `GET http://localhost:8099/swarm/task_status/<task_id>`
   - Agent Load: `GET http://localhost:8099/swarm/agent_load`
   - Redistribute Tasks: `POST http://localhost:8099/swarm/redistribute_tasks`
   - Swarm Statistics: `GET http://localhost:8099/swarm/statistics`
   - Scale Agents: `POST http://localhost:8099/agents/scale`

3. Create and place workflow YAML files in the `workflows` directory. The system will automatically load and execute these workflows.

## API Usage Examples

### Adding a Task

```bash
curl -X POST http://localhost:8099/swarm/add_task \
  -H "Content-Type: application/json" \
  -d '{"description": "Complex math calculation", "priority": 8, "specialization": "math"}'
```

### Getting Swarm State

```bash
curl http://localhost:8099/swarm/state
```

### Checking Task Status

```bash
curl http://localhost:8099/swarm/task_status/1
```

### Redistributing Tasks

```bash
curl -X POST http://localhost:8099/swarm/redistribute_tasks \
  -H "Content-Type: application/json" \
  -d '{"threshold": 5}'
```

### Getting Swarm Statistics

```bash
curl http://localhost:8099/swarm/statistics
```

### Scaling Agents

```bash
curl -X POST http://localhost:8099/agents/scale \
  -H "Content-Type: application/json" \
  -d '{"num_agents": 2}'
```

## Architecture

The integrated BYOAI-Swarm system consists of the following main components:

1. **BYOAI Script (`byoai-script.py`)**: The main entry point that initializes the system, loads workflows, and starts the Flask server.

2. **Swarm Integration (`swarm_integration.py`)**: Implements the core Swarm functionality, including task management, agent specializations, and decentralized task execution.

3. **Workflows**: YAML files defining task sequences, priorities, and specializations.

4. **Flask API**: Provides endpoints for system interaction and monitoring.

5. **Dynamic Agent Scaling**: Automatically scales the number of agents based on the current workload.

## Workflow Structure

Workflows are defined in YAML files with the following structure:

```yaml
name: Sample Workflow
steps:
  - name: Task Name
    action: action_to_perform
    priority: 5
    specialization: math
```

## Error Handling

The API provides clear error messages for various scenarios:

- Invalid JSON payload
- Missing required fields
- Task not found
- Internal server errors

Error responses include a JSON object with an "error" key containing a descriptive message.

## Logging and Monitoring

The system provides detailed logging for all operations, including:

- Task addition and execution
- Agent registration and task assignment
- Workflow loading and execution
- API requests and responses
- Dynamic agent scaling

Logs can be found in the console output when running the application.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
