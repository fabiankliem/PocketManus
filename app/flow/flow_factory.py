"""
Factory for creating different types of flows.

This module provides a factory class for creating and configuring various types
of flows, including integration with PocketFlow.
"""
from typing import Dict, List, Optional, Union

from app.agent.base import BaseAgent
from app.flow.base import BaseFlow, FlowType
from app.flow.planning import PlanningFlow
from app.tool.base import BaseTool

# Import PocketFlow integration if available
try:
    from app.pocketflow.adapters import OpenManusFlowAdapter
    from app.pocketflow.orchestrator import WorkflowOrchestrator
    POCKETFLOW_AVAILABLE = True
except ImportError:
    POCKETFLOW_AVAILABLE = False


class FlowFactory:
    """Factory for creating different types of flows with support for multiple agents"""

    @staticmethod
    def create_flow(
        flow_type: FlowType,
        agents: Union[BaseAgent, List[BaseAgent], Dict[str, BaseAgent]],
        **kwargs,
    ) -> BaseFlow:
        flows = {
            FlowType.PLANNING: PlanningFlow,
        }

        flow_class = flows.get(flow_type)
        if not flow_class:
            raise ValueError(f"Unknown flow type: {flow_type}")

        return flow_class(agents, **kwargs)
    
    @staticmethod
    def create_pocketflow_based_flow(
        flow_type: str,
        agents: List[BaseAgent],
        tools: Optional[List[BaseTool]] = None,
        connections: Optional[Dict[str, List[str]]] = None,
        name: Optional[str] = None
    ) -> BaseFlow:
        """
        Create a flow based on PocketFlow architecture.
        
        Args:
            flow_type: Type of flow to create ("agent", "planning", or "hybrid")
            agents: Agents to include in the flow
            tools: Tools to include in the flow
            connections: Optional connection mapping for agents/nodes
            name: Optional name for the flow
            
        Returns:
            A flow based on PocketFlow architecture, adapted for Open Manus
            
        Raises:
            ImportError: If PocketFlow integration is not available
            ValueError: If an invalid flow_type is specified
        """
        if not POCKETFLOW_AVAILABLE:
            raise ImportError(
                "PocketFlow integration not available. "
                "Please install PocketFlow and ensure the app.pocketflow module is available."
            )
        
        # Create orchestrator
        orchestrator = WorkflowOrchestrator()
        
        # Register all tools
        if tools:
            for tool in tools:
                orchestrator.register_tool(tool)
        
        # Create the appropriate flow type
        flow_name = name or f"{flow_type.capitalize()}Flow"
        
        if flow_type.lower() == "agent":
            if not agents:
                raise ValueError("At least one agent must be provided for an agent flow")
                
            # Create an agent workflow
            pf_flow = orchestrator.create_agent_workflow(
                agents=agents,
                connections=connections,
                flow_name=flow_name
            )
            
            # Adapt for Open Manus
            return OpenManusFlowAdapter(
                flow=pf_flow,
                name=flow_name,
                description=f"PocketFlow-based agent workflow with {len(agents)} agents"
            )
            
        elif flow_type.lower() == "planning":
            if not agents or len(agents) != 1:
                raise ValueError("Exactly one planning agent must be provided for a planning flow")
                
            # Create a planning workflow
            return orchestrator.create_planning_workflow(
                planner_agent=agents[0],
                execution_tools=tools,
                flow_name=flow_name
            )
            
        elif flow_type.lower() == "hybrid":
            if not agents or len(agents) < 2:
                raise ValueError("At least one planning agent and one execution agent must be provided")
                
            # First agent is the planner, rest are execution agents
            planning_agent = agents[0]
            execution_agents = agents[1:]
            
            # Create a hybrid workflow
            pf_flow = orchestrator.create_hybrid_workflow(
                planning_agent=planning_agent,
                execution_agents=execution_agents,
                execution_tools=tools,
                flow_name=flow_name
            )
            
            # Adapt for Open Manus
            return OpenManusFlowAdapter(
                flow=pf_flow,
                name=flow_name,
                description=f"PocketFlow-based hybrid workflow with planning and {len(execution_agents)} execution agents"
            )
            
        else:
            raise ValueError(f"Invalid flow type: {flow_type}")
