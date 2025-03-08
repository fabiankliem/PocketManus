#!/usr/bin/env python3
"""
Example based on PocketFlow documentation.
"""
import time
from typing import Dict, Any

from pocketflow_framework import Node, Flow


class SimpleNode(Node):
    """Simple node implementation."""
    
    def __init__(self, name="node", max_retries=1, wait=0):
        """Initialize the node."""
        super().__init__(max_retries=max_retries, wait=wait)
        self.name = name
        self.successors = {}
    
    def add_successor(self, node, key="default"):
        """Add a successor node."""
        self.successors[key] = node
        return self
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data."""
        print(f"[{self.name}] Preparing...")
        return {"name": self.name}
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Execute node."""
        print(f"[{self.name}] Executing with {prep_res}...")
        time.sleep(1)
        return "default"  # This is the key to look up in successors
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> Dict[str, Any]:
        """Post-process results."""
        print(f"[{self.name}] Post-processing with exec_res={exec_res}...")
        shared[f"{self.name}_completed"] = True
        return shared


def main():
    """Run the example workflow."""
    print("\n=== PocketFlow Documentation Example ===\n")
    
    # Create nodes
    node1 = SimpleNode("research")
    node2 = SimpleNode("generation")
    node3 = SimpleNode("optimization")
    
    # Connect nodes
    node1.add_successor(node2)
    node2.add_successor(node3)
    
    # Create flow
    flow = Flow(node1)
    
    # Run the workflow
    print("Running workflow...")
    result = flow.run({})
    
    print("\nWorkflow completed!")
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
