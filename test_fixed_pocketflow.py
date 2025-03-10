#!/usr/bin/env python3
"""
Test script for the fixed PocketFlow integration.

This script demonstrates the integration of PocketFlow and Open Manus,
showing how the various components work together to create and run workflows.
"""
import asyncio
import json
import sys
import os
from typing import Dict, Any

# Import PocketFlow components
from app.pocketflow.fixed_orchestrator import WorkflowOrchestrator
from app.pocketflow.fixed_adapters import ToolNode, AgentNode

# Import agents and tools
from app.agent.planning_mock import PlanningAgent
from app.agent.react import ReActAgent
from app.tool.bash import Bash
from app.tool.google_search import GoogleSearch
from app.tool.str_replace_editor import StrReplaceEditor


class SimpleReActAgent(ReActAgent):
    """A simple ReAct agent for testing."""
    
    def __init__(self, name: str = "react_agent"):
        """Initialize a simple ReAct agent."""
        super().__init__(name=name)
        self.system_prompt = f"""
        You are a helpful assistant named {name}.
        """
        self.tools = []
    
    def add_tool(self, tool):
        """Add a tool to the agent."""
        self.tools.append(tool)
    
    async def think(self):
        """Think about the next step."""
        # Simple implementation for testing
        return False
    
    async def act(self):
        """Perform an action."""
        # Simple implementation for testing
        return "Action completed successfully."


async def test_sequential_workflow():
    """Test a sequential workflow with tools."""
    print("\n=== Testing Sequential Workflow ===\n")
    
    # Initialize the orchestrator
    orchestrator = WorkflowOrchestrator()
    
    # Register tools
    search_tool = GoogleSearch()
    bash_tool = Bash()
    editor_tool = StrReplaceEditor()
    
    orchestrator.register_tool(search_tool)
    orchestrator.register_tool(bash_tool)
    orchestrator.register_tool(editor_tool)
    
    # Create nodes for each tool
    search_node = orchestrator.create_tool_node(search_tool.name, "search_result")
    bash_node = orchestrator.create_tool_node(bash_tool.name, "bash_result")
    editor_node = orchestrator.create_tool_node(editor_tool.name, "editor_result")
    
    # Create a sequential workflow
    workflow = orchestrator.create_sequential_workflow(
        nodes=[search_node, bash_node, editor_node],
        flow_name="SequentialWorkflow"
    )
    
    # Prepare input data
    inputs = {
        "query": "Python async programming",
        "command": "echo 'Hello, World!'",
        "file_path": "test.txt",
        "old_content": "Hello",
        "new_content": "Hello, World!"
    }
    
    # Run the workflow
    print("Running sequential workflow...")
    result = workflow.run(inputs)
    
    # Display results
    print("\nWorkflow completed!")
    print("\nResults:")
    for key, value in result.items():
        print(f"{key}: {value}")


async def test_agent_workflow():
    """Test a workflow with agents."""
    print("\n=== Testing Agent Workflow ===\n")
    
    # Initialize the orchestrator
    orchestrator = WorkflowOrchestrator()
    
    # Create agents
    planning_agent = PlanningAgent(name="planner")
    react_agent = SimpleReActAgent(name="reactor")
    
    # Register tools for the react agent
    search_tool = SearchTool()
    bash_tool = BashTool()
    react_agent.add_tool(search_tool)
    react_agent.add_tool(bash_tool)
    
    # Register agents
    orchestrator.register_agent(planning_agent)
    orchestrator.register_agent(react_agent)
    
    # Create nodes for each agent
    planner_node = orchestrator.create_agent_node(planning_agent.name, "plan")
    reactor_node = orchestrator.create_agent_node(react_agent.name, "reaction")
    
    # Create a sequential workflow
    workflow = orchestrator.create_sequential_workflow(
        nodes=[planner_node, reactor_node],
        flow_name="AgentWorkflow"
    )
    
    # Prepare input data
    inputs = {
        "task": "Create a Python script that prints 'Hello, World!'",
        "context": {"language": "Python", "level": "beginner"}
    }
    
    # Run the workflow
    print("Running agent workflow...")
    result = workflow.run(inputs)
    
    # Display results
    print("\nWorkflow completed!")
    print("\nResults:")
    for key, value in result.items():
        print(f"{key}: {value}")


async def test_branching_workflow():
    """Test a branching workflow."""
    print("\n=== Testing Branching Workflow ===\n")
    
    # Initialize the orchestrator
    orchestrator = WorkflowOrchestrator()
    
    # Register tools
    search_tool = GoogleSearch()
    bash_tool = Bash()
    editor_tool = StrReplaceEditor()
    
    orchestrator.register_tool(search_tool)
    orchestrator.register_tool(bash_tool)
    orchestrator.register_tool(editor_tool)
    
    # Create nodes for each tool
    search_node = orchestrator.create_tool_node(search_tool.name, "search_result")
    bash_node = orchestrator.create_tool_node(bash_tool.name, "bash_result")
    editor_node = orchestrator.create_tool_node(editor_tool.name, "editor_result")
    
    # Create a branching workflow
    nodes = {
        "search": search_node,
        "bash": bash_node,
        "editor": editor_node
    }
    
    connections = {
        "search": {
            "default": "bash",
            "error": "editor"
        },
        "bash": {
            "default": "editor"
        }
    }
    
    workflow = orchestrator.create_branching_workflow(
        nodes=nodes,
        connections=connections,
        start_node="search",
        flow_name="BranchingWorkflow"
    )
    
    # Prepare input data
    inputs = {
        "query": "Python async programming",
        "command": "echo 'Hello, World!'",
        "file_path": "test.txt",
        "old_content": "Hello",
        "new_content": "Hello, World!"
    }
    
    # Run the workflow
    print("Running branching workflow...")
    result = workflow.run(inputs)
    
    # Display results
    print("\nWorkflow completed!")
    print("\nResults:")
    for key, value in result.items():
        print(f"{key}: {value}")


async def main():
    """Run all tests."""
    try:
        await test_sequential_workflow()
        await test_agent_workflow()
        await test_branching_workflow()
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
