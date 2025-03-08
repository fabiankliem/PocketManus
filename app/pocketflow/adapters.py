"""
Adapter classes to bridge PocketFlow and Open Manus components.

These adapters enable bidirectional compatibility between PocketFlow's Node/Flow
architecture and Open Manus's agent and tool systems.
"""
from typing import Any, Dict, List, Optional, Union, Callable

# Import PocketFlow dependencies
import sys
sys.path.append('PocketFlow')
from pocketflow import Node, Flow

# Import Open Manus dependencies
from app.agent.base import BaseAgent
from app.tool.base import BaseTool
from app.flow.base import BaseFlow


class PocketFlowNodeAdapter(Node):
    """Adapts Open Manus tools and agents to work as PocketFlow Nodes."""
    
    def __init__(
        self, 
        tool_or_agent: Union[BaseTool, BaseAgent],
        input_keys: List[str] = None,
        output_key: str = None,
        name: str = None
    ):
        """
        Initialize a PocketFlow Node that wraps an Open Manus tool or agent.
        
        Args:
            tool_or_agent: Open Manus tool or agent to adapt
            input_keys: Keys to extract from store for tool/agent input
            output_key: Key to store the tool/agent output
            name: Optional name for the node
        """
        self.tool_or_agent = tool_or_agent
        self.input_keys = input_keys or []
        self.output_key = output_key or "result"
        super().__init__(name=name or tool_or_agent.__class__.__name__)
        
    def prep(self, store: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant data from store for tool/agent execution."""
        inputs = {key: store.get(key) for key in self.input_keys if key in store}
        return inputs
    
    def exec(self, data: Dict[str, Any]) -> Any:
        """Execute the Open Manus tool or agent with the provided data."""
        if isinstance(self.tool_or_agent, BaseTool):
            return self.tool_or_agent.run(**data)
        elif isinstance(self.tool_or_agent, BaseAgent):
            # For agents, we need to determine the appropriate method to call
            if hasattr(self.tool_or_agent, 'step'):
                return self.tool_or_agent.step(data)
            else:
                return self.tool_or_agent.run(data)
        else:
            raise TypeError(f"Unsupported type: {type(self.tool_or_agent)}")
    
    def post(self, result: Any, store: Dict[str, Any]) -> Dict[str, Any]:
        """Process result and update the shared store."""
        store[self.output_key] = result
        return store


class OpenManusToolAdapter(BaseTool):
    """Adapts a PocketFlow Node to work as an Open Manus Tool."""
    
    def __init__(
        self, 
        node: Node,
        name: str = None,
        description: str = None
    ):
        """
        Initialize an Open Manus Tool that wraps a PocketFlow Node.
        
        Args:
            node: PocketFlow Node to adapt
            name: Optional name for the tool
            description: Optional description of the tool
        """
        self.node = node
        self.store = {}  # Internal store for the node
        
        super().__init__(
            name=name or node.name,
            description=description or f"PocketFlow Node adapter for {node.name}"
        )
    
    def run(self, **kwargs) -> Any:
        """Execute the PocketFlow Node with the provided inputs."""
        # Update internal store with inputs
        self.store.update(kwargs)
        
        # Execute node's lifecycle
        inputs = self.node.prep(self.store)
        result = self.node.exec(inputs)
        self.store = self.node.post(result, self.store)
        
        return result


class PocketFlowAdapter:
    """Utility class for creating and managing PocketFlow integrations."""
    
    @staticmethod
    def create_flow_from_tools(
        tools: List[BaseTool],
        flow_name: str = "ToolFlow",
        connections: Dict[str, List[str]] = None
    ) -> Flow:
        """
        Create a PocketFlow Flow from a list of Open Manus tools.
        
        Args:
            tools: List of Open Manus tools to include in the flow
            flow_name: Name for the created flow
            connections: Optional dict mapping source nodes to target nodes
                        If None, tools will be connected sequentially
        
        Returns:
            A PocketFlow Flow object with all tools as nodes
        """
        nodes = [PocketFlowNodeAdapter(tool) for tool in tools]
        flow = Flow(nodes=nodes, name=flow_name)
        
        # Configure connections
        if connections:
            for source, targets in connections.items():
                for target in targets:
                    flow.connect(source, target)
        else:
            # Sequential connection
            for i in range(len(nodes) - 1):
                flow.connect(nodes[i].name, nodes[i + 1].name)
                
        return flow


class OpenManusFlowAdapter(BaseFlow):
    """Adapts a PocketFlow Flow to work as an Open Manus Flow."""
    
    def __init__(
        self, 
        flow: Flow,
        name: str = None,
        description: str = None
    ):
        """
        Initialize an Open Manus Flow that wraps a PocketFlow Flow.
        
        Args:
            flow: PocketFlow Flow to adapt
            name: Optional name for the flow
            description: Optional description for the flow
        """
        self.flow = flow
        self.store = {}  # Shared store for the flow
        
        super().__init__(
            name=name or flow.name,
            description=description or f"PocketFlow Flow adapter for {flow.name}"
        )
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Execute the PocketFlow Flow with the provided inputs."""
        # Update store with inputs
        self.store.update(kwargs)
        
        # Execute the flow
        result = self.flow.run(self.store)
        
        return result