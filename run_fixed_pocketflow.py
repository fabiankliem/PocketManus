#!/usr/bin/env python3
"""
Run a workflow using the fixed PocketFlow and Open Manus integration.

This script provides a command-line interface for running various integrated workflows
between PocketFlow and Open Manus, using the fixed implementation that avoids
circular dependencies and execution issues.
"""
import argparse
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

# Import agents
from app.agent.planning_mock import PlanningAgent
from app.agent.react import ReActAgent
from app.agent.planning import PlanningAgent as FullPlanningAgent

# Import tools
from app.tool.bash import Bash
from app.tool.web_search import WebSearch
from app.tool.str_replace_editor import StrReplaceEditor

# Import fixed PocketFlow integration
from app.pocketflow.fixed_orchestrator import WorkflowOrchestrator, CustomFlow
from app.pocketflow.fixed_adapters import ToolNode, AgentNode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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


class ExampleWorkflows:
    """Collection of example workflows using the fixed PocketFlow integration."""
    
    @staticmethod
    async def run_multi_agent_workflow(
        task: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Run a multi-agent workflow that coordinates planning, research, and code execution.
        
        This example creates a workflow with three agents:
        1. Planning agent - creates a plan for solving the task
        2. Research agent - gathers information needed for the task
        3. Execution agent - implements the solution based on research and planning
        
        Args:
            task: The task to complete
            context: Additional context for the task
            
        Returns:
            The results from the workflow execution
        """
        # Initialize the orchestrator
        orchestrator = WorkflowOrchestrator()
        
        # Create agents
        planning_agent = PlanningAgent(name="planner")
        research_agent = SimpleReActAgent(name="researcher")
        execution_agent = SimpleReActAgent(name="executor")
        
        # Create tools
        search_tool = WebSearch()
        bash_tool = Bash()
        editor_tool = StrReplaceEditor()
        
        # Add tools to agents
        research_agent.add_tool(search_tool)
        execution_agent.add_tool(bash_tool)
        execution_agent.add_tool(editor_tool)
        
        # Register tools and agents
        orchestrator.register_tool(search_tool)
        orchestrator.register_tool(bash_tool)
        orchestrator.register_tool(editor_tool)
        
        orchestrator.register_agent(planning_agent)
        orchestrator.register_agent(research_agent)
        orchestrator.register_agent(execution_agent)
        
        # Create a workflow
        workflow = orchestrator.create_agent_workflow(
            agents=[planning_agent, research_agent, execution_agent],
            connections={
                "planner": ["researcher"],
                "researcher": ["executor"]
            },
            flow_name="MultiAgentWorkflow"
        )
        
        # Run the workflow
        result = orchestrator.run_workflow(
            workflow_name="MultiAgentWorkflow",
            inputs={"task": task, "context": context or {}}
        )
        
        return result
    
    @staticmethod
    async def run_planning_with_parallel_execution(
        task: str,
        tools: List[Any] = None
    ) -> Dict[str, Any]:
        """
        Run a workflow that uses planning to create a parallel execution plan.
        
        This example creates a workflow where a planning agent creates a plan with
        tasks that can be executed in parallel, and then executes them.
        
        Args:
            task: The task to complete
            tools: Optional list of tools to use for execution
            
        Returns:
            The results from the workflow execution
        """
        # Initialize the orchestrator
        orchestrator = WorkflowOrchestrator()
        
        # Create agents
        planning_agent = FullPlanningAgent(name="planner")
        execution_agent = SimpleReActAgent(name="executor")
        
        # Create tools if not provided
        if not tools:
            tools = [
                WebSearch(),
                Bash(),
                StrReplaceEditor()
            ]
        
        # Add tools to agents
        for tool in tools:
            execution_agent.add_tool(tool)
            orchestrator.register_tool(tool)
        
        # Register agents
        orchestrator.register_agent(planning_agent)
        orchestrator.register_agent(execution_agent)
        
        # Create nodes
        planner_node = orchestrator.create_agent_node(planning_agent.name, "plan")
        executor_node = orchestrator.create_agent_node(execution_agent.name, "execution_result")
        
        # Create a sequential workflow
        workflow = orchestrator.create_sequential_workflow(
            nodes=[planner_node, executor_node],
            flow_name="PlanningWorkflow"
        )
        
        # Run the workflow
        result = orchestrator.run_workflow(
            workflow_name="PlanningWorkflow",
            inputs={"task": task}
        )
        
        return result


async def main():
    """Main entry point for the workflow runner."""
    parser = argparse.ArgumentParser(description="Run integrated PocketFlow-OpenManus workflows")
    parser.add_argument(
        "--workflow", 
        type=str, 
        default="multi_agent",
        choices=["multi_agent", "planning"],
        help="Type of workflow to run"
    )
    parser.add_argument(
        "--task", 
        type=str, 
        default="Create a simple Python script that prints 'Hello, World!'",
        help="Task to complete"
    )
    parser.add_argument(
        "--context", 
        type=str, 
        default=None,
        help="JSON string with additional context for the task"
    )
    args = parser.parse_args()
    
    # Parse context if provided
    context = None
    if args.context:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON context: {args.context}")
            return
    
    # Run the selected workflow
    try:
        if args.workflow == "multi_agent":
            logger.info(f"Running multi-agent workflow for task: {args.task}")
            result = await ExampleWorkflows.run_multi_agent_workflow(
                task=args.task,
                context=context
            )
        elif args.workflow == "planning":
            logger.info(f"Running planning workflow for task: {args.task}")
            result = await ExampleWorkflows.run_planning_with_parallel_execution(
                task=args.task
            )
        else:
            logger.error(f"Unknown workflow type: {args.workflow}")
            return
        
        # Display results
        logger.info("Workflow completed successfully!")
        logger.info("Results:")
        for key, value in result.items():
            logger.info(f"{key}: {value}")
    except Exception as e:
        logger.error(f"Error running workflow: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
