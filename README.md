# Open Manus with PocketFlow Integration

This repository extends the Open Manus project with PocketFlow(https://github.com/The-Pocket-World/Pocket-Flow-Framework) integration for orchestrating complex agent workflows.

## Features

- **PocketFlow Integration**: Lightweight workflow orchestration with Open Manus agents
- **Bidirectional Adapters**: Use Open Manus tools/agents as PocketFlow nodes and vice versa
- **Workflow Orchestration**: Multi-agent workflows with structured control flow
- **Hybrid Planning**: Combine planning and execution agents flexibly

## Installing PocketFlow Framework

```bash
pip install pocketflow_framework
```

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/The-Pocket-World/PocketManus.git
cd PocketManus
```

2. Install dependencies and PocketFlow:
```bash
pip install -r requirements.txt
pip install pocketflow_framework
```

3. Set up your configuration file:
```bash
cp config/config.example.toml config/config.toml
```

### Configuration Setup

Edit `config/config.toml` with your API keys and settings:

```toml
# Global LLM configuration
[llm]
model = "gpt-4o"                     # The LLM model to use
base_url = "https://api.openai.com/v1" # API endpoint URL
api_key = "YOUR_API_KEY"             # Your API key
max_tokens = 4096                    # Maximum number of tokens in the response
temperature = 0.0                    # Controls randomness

# Optional configuration for specific LLM models
[llm.vision]
model = "gpt-4o"                     # The vision model to use
base_url = "https://api.openai.com/v1" # API endpoint URL for vision model
api_key = "YOUR_API_KEY"             # Your API key for vision model

# Add PocketFlow specific configuration
[pocketflow]
log_level = "INFO"
```

## Running Example Workflows

```bash
# Multi-agent workflow
python run_fixed_pocketflow.py --workflow multi_agent --task "Create a Python script that analyzes stock data"

# Planning workflow with parallel execution
python run_fixed_pocketflow.py --workflow planning_parallel --task "Research and summarize the latest AI trends"

# RAG workflow
python run_fixed_pocketflow.py --workflow rag --query "How does transformer architecture work?" --documents documents.json
```

See example applications in the `examples/` directory.

## Creating Custom Workflows

```python
from app.pocketflow.fixed_orchestrator import WorkflowOrchestrator
from app.agent.planning import PlanningAgent
from app.agent.react import ReactAgent

# Create and register agents
orchestrator = WorkflowOrchestrator()
orchestrator.register_agent(PlanningAgent(), "planner")
orchestrator.register_agent(ReactAgent(), "executor")

# Create and run workflow
workflow = orchestrator.create_agent_workflow(
    agents=["planner", "executor"],
    flow_name="CustomWorkflow"
)

result = orchestrator.run_workflow(
    workflow_name="CustomWorkflow",
    inputs={"task": "Your task here"}
)
```

## Architecture

- **Adapters**: Bridge between PocketFlow and Open Manus components
- **Orchestrator**: Manages workflows and provides a unified interface
- **Flow Factory**: Creates PocketFlow-based flows with agent, planning, and hybrid patterns

## PocketFlow Framework

PocketFlow is a lightweight workflow orchestration system for AI agent workflows with:

- Node-based architecture for workflows
- Support for sequential, parallel, and conditional flows
- Easy integration with existing systems

The framework uses nodes (computation units), edges (connections), and flows (complete workflows) to enable flexible agent orchestration patterns.

## Acknowledgements

Thanks to the OpenManus team for their innovative agent architecture.

## License

This project is licensed under the terms specified in the LICENSE file.
