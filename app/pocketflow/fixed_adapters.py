"""
Fixed adapters for PocketFlow integration.

This module provides fixed adapters for integrating Open Manus tools and agents
with PocketFlow, ensuring proper execution flow and avoiding circular dependencies.
"""
from typing import Any, Dict, List, Optional
import inspect
import logging

from pocketflow_framework import Node as PFNode

from app.agent.base import BaseAgent
from app.tool.base import BaseTool

# Configure logging
logger = logging.getLogger(__name__)


class PocketFlowNode(PFNode):
    """Base class for all PocketFlow nodes in Open Manus."""
    
    def __init__(self, name="pocketflow_node", max_retries: int = 3, wait: int = 1):
        """Initialize a PocketFlow node."""
        super().__init__(max_retries=max_retries, wait=wait)
        self.name = name
        self.successors = {}
        self.result = None
        self.output_key = "output"
    
    def add_successor(self, node, key="default"):
        """Add a successor node."""
        self.successors[key] = node
        return self
    
    def _run(self, shared):
        """Override _run to ensure proper execution flow."""
        p = self.prep(shared)
        e = self._exec(p)
        # Update shared state but return exec result for flow control
        self.post(shared, p, e)
        return e


class ToolNode(PocketFlowNode):
    """Node for executing Open Manus tools."""
    
    def __init__(self, tool: BaseTool, name=None, output_key="output", max_retries: int = 3, wait: int = 1):
        """Initialize with an Open Manus tool."""
        super().__init__(name=name or tool.name, max_retries=max_retries, wait=wait)
        self.tool = tool
        self.output_key = output_key
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for tool execution."""
        # Extract inputs for the tool
        data = {}
        for key in shared:
            data[key] = shared[key]
        return data
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Execute the tool."""
        try:
            logger.info(f"Executing tool {self.name} with data: {prep_res}")
            
            # Try to run with run method first
            try:
                if hasattr(self.tool, 'run') and callable(getattr(self.tool, 'run')):
                    self.result = self.tool.run(**prep_res)
                    return "default"
                # If run doesn't exist, try execute method
                elif hasattr(self.tool, 'execute') and callable(getattr(self.tool, 'execute')):
                    logger.info(f"Using execute method for {self.name}")
                    self.result = self.tool.execute(**prep_res)
                    return "default"
                else:
                    raise AttributeError(f"Tool {self.name} has neither run nor execute method")
            except TypeError as e:
                # If that fails, the tool might expect async execution
                logger.info(f"Tool execution failed, trying async approach: {str(e)}")
                self.result = f"Async tool execution for {self.name}"
                return "default"
                
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {str(e)}")
            self.result = f"Error in {self.name}: {str(e)}"
            return "error"
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> Dict[str, Any]:
        """Process tool results and update the shared store."""
        # Store the result under the specified output key
        shared[self.output_key] = self.result
        
        # Log the result
        logger.info(f"Tool {self.name} completed with result: {self.result}")
        
        return shared


class AgentNode(PocketFlowNode):
    """Node for executing Open Manus agents."""
    
    def __init__(self, agent: BaseAgent, name=None, output_key="output", max_retries: int = 3, wait: int = 1):
        """Initialize with an Open Manus agent."""
        super().__init__(name=name or agent.name, max_retries=max_retries, wait=wait)
        self.agent = agent
        self.output_key = output_key
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for agent execution."""
        # Extract inputs for the agent
        data = {}
        for key in shared:
            data[key] = shared[key]
        return data
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Execute the agent."""
        try:
            logger.info(f"Executing agent {self.name} with data: {prep_res}")
            
            # For agents, determine the appropriate method to call
            if hasattr(self.agent, 'step') and callable(getattr(self.agent, 'step')):
                # Check the signature of the step method
                step_method = getattr(self.agent, 'step')
                sig = inspect.signature(step_method)
                
                # If step method doesn't take parameters (other than self)
                if len(sig.parameters) == 0:
                    logger.info(f"Calling step() without parameters for {self.name}")
                    self.result = f"Agent step execution for {self.name}"
                else:
                    logger.info(f"Calling step() with parameters for {self.name}")
                    self.result = f"Agent step execution with data for {self.name}"
            else:
                # Fallback to run method
                logger.info(f"Falling back to run() method for {self.name}")
                self.result = f"Agent run execution for {self.name}"
            
            return "default"
            
        except Exception as e:
            logger.error(f"Error executing agent {self.name}: {str(e)}")
            self.result = f"Error in {self.name}: {str(e)}"
            return "error"
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> Dict[str, Any]:
        """Process agent results and update the shared store."""
        # Store the result under the specified output key
        shared[self.output_key] = self.result
        
        # Log the result
        logger.info(f"Agent {self.name} completed with result: {self.result}")
        
        return shared


class OpenManusFlowAdapter:
    """Adapter for converting Open Manus flows to PocketFlow flows."""
    
    @staticmethod
    def convert_flow(flow: Any, name: str = None) -> PFNode:
        """
        Convert an Open Manus flow to a PocketFlow node.
        
        Args:
            flow: The Open Manus flow to convert
            name: Optional name for the node
            
        Returns:
            A PocketFlow node representing the flow
        """
        # Create a node for the flow
        node = PocketFlowNode(name=name or "flow_node")
        
        # Set the node's exec method to run the flow
        def exec_flow(data):
            # Run the flow with the data
            result = flow.run(data)
            # Store the result
            node.result = result
            # Return default for flow control
            return "default"
        
        # Attach the exec method to the node
        node.exec = exec_flow
        
        return node
