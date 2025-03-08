# Open Manus with PocketFlow Integration

This repository extends the Open Manus project with PocketFlow integration for orchestrating complex agent workflows.

## Features

- **PocketFlow Integration**: Leverage PocketFlow's lightweight workflow orchestration system with Open Manus agents
- **Bidirectional Adapters**: Use Open Manus tools/agents as PocketFlow nodes and vice versa
- **Workflow Orchestration**: Create complex multi-agent workflows with structured control flow
- **Hybrid Planning**: Combine planning agents with execution agents in flexible patterns

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/yourusername/open-manus-2.git
cd open-manus-2
```

2. Clone the PocketFlow submodule:
```bash
git clone https://github.com/LangChain-Tutorials/pocketflow.git PocketFlow
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your configuration file:
```bash
cp config/config.example.toml config/config.toml
# Edit config/config.toml with your LLM API keys
```

## Running Example Workflows

You can run the provided example workflows:

```bash
# Run a multi-agent workflow
python run_pocketflow.py --workflow multi_agent --task "Create a Python script that analyzes stock data"

# Run a planning workflow with parallel execution
python run_pocketflow.py --workflow planning_parallel --task "Research and summarize the latest AI trends"

# Run a RAG workflow
python run_pocketflow.py --workflow rag --query "How does transformer architecture work?" --documents documents.json
```

## Creating Custom Workflows

You can create custom workflows by extending the integration:

```python
from app.pocketflow.orchestrator import WorkflowOrchestrator
from app.agent.planning import PlanningAgent
from app.agent.react import ReactAgent

# Create orchestrator
orchestrator = WorkflowOrchestrator()

# Register agents
planning_agent = PlanningAgent()
execution_agent = ReactAgent()

orchestrator.register_agent(planning_agent, "planner")
orchestrator.register_agent(execution_agent, "executor")

# Create a workflow
workflow = orchestrator.create_agent_workflow(
    agents=[planning_agent, execution_agent],
    flow_name="CustomWorkflow"
)

# Run workflow
result = await orchestrator.run_workflow(
    workflow_name="CustomWorkflow",
    inputs={"task": "Your task here"}
)
```

## Architecture

The integration is built on these key components:

1. **Adapters**: Bridge between PocketFlow and Open Manus components
   - `PocketFlowNodeAdapter`: Adapts Open Manus tools/agents to PocketFlow nodes
   - `OpenManusToolAdapter`: Adapts PocketFlow nodes to Open Manus tools
   - `OpenManusFlowAdapter`: Adapts PocketFlow flows to Open Manus flows

2. **Orchestrator**: Manages workflows and provides a unified interface
   - Registration of agents, tools, and flows
   - Creation of different workflow types
   - Execution of workflows with state management

3. **Flow Factory**: Factory extensions for creating PocketFlow-based flows
   - Support for agent, planning, and hybrid flows
   - Integration with Open Manus's existing flow system

## License

This project is licensed under the terms specified in the LICENSE file.