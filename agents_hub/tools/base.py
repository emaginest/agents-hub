"""
Base Tool interface for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union, Callable
from pydantic import BaseModel, Field


class BaseTool:
    """
    Base class for tools.
    
    This abstract class defines the interface that all tools must implement.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
    ):
        """
        Initialize a tool.
        
        Args:
            name: Name of the tool
            description: Description of what the tool does
            parameters: JSON Schema for the tool's parameters
        """
        self.name = name
        self.description = description
        self.parameters = parameters
    
    async def run(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Run the tool with the given parameters.
        
        Args:
            parameters: Parameters for the tool
            context: Optional context information
            
        Returns:
            Result of running the tool
        """
        raise NotImplementedError("Subclasses must implement run()")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tool to a dictionary representation.
        
        Returns:
            Dictionary representation of the tool
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
