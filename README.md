# BYOAI with Swarm Integration

## Introduction

This project integrates the BYOAI (Bring Your Own AI) framework with OpenAI's Swarm, creating a powerful, decentralized, and context-driven agent system. By combining these technologies, we've created a flexible and scalable solution for distributed task execution and AI-driven workflows.

## Features

- Decentralized agent architecture
- Context-driven task distribution
- Specialization-based task assignment
- Priority queue for efficient task management
- RESTful API for task submission and status monitoring
- Seamless integration of BYOAI and Swarm concepts

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
   export CONTEXT_AGENT_PORT=8000
   export CONTEXT_AGENT_HOST=0.0.0.0
   ```

## Usage

1. Start the BYOAI-Swarm system:
   ```
   python byoai-script.py
   ```

2. Access the API endpoints:
   - Home: `http://localhost:8000/`
   - Status: `http://localhost:8000/status`
   - Swarm State: `http://localhost:8000/swarm/state`
   - Add Task: `POST http://localhost:8000/swarm/add_task`

3. Create and place workflow YAML files in the `workflows` directory. The system will automatically load and execute these workflows.

## Architecture

The integrated BYOAI-Swarm system consists of the following main components:

1. **BYOAI Script (`byoai-script.py`)**: The main entry point that initializes the system, loads workflows, and starts the Flask server.

2. **Swarm Integration (`swarm_integration.py`)**: Implements the core Swarm functionality, including task management, agent specializations, and decentralized task execution.

3. **Workflows**: YAML files defining task sequences, priorities, and specializations.

4. **Flask API**: Provides endpoints for system interaction and monitoring.

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

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
