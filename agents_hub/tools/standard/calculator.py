"""
Calculator tool for the Agents Hub framework.
"""

from typing import Dict, Any, Optional
import math
import re
from agents_hub.tools.base import BaseTool


class CalculatorTool(BaseTool):
    """
    Calculator tool for performing mathematical calculations.
    """
    
    def __init__(self):
        """Initialize the calculator tool."""
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate",
                    }
                },
                "required": ["expression"],
            },
        )
    
    async def run(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Evaluate a mathematical expression.
        
        Args:
            parameters: Parameters for the tool
            context: Optional context information
            
        Returns:
            Result of the calculation
        """
        expression = parameters.get("expression", "")
        
        # Sanitize the expression to prevent code injection
        sanitized_expression = self._sanitize_expression(expression)
        
        try:
            # Create a safe environment with only math functions
            safe_env = {
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                "pow": pow,
                "math": math,
            }
            
            # Evaluate the expression
            result = eval(sanitized_expression, {"__builtins__": {}}, safe_env)
            
            return {
                "result": result,
                "expression": expression,
            }
        except Exception as e:
            return {
                "error": str(e),
                "expression": expression,
            }
    
    def _sanitize_expression(self, expression: str) -> str:
        """
        Sanitize a mathematical expression to prevent code injection.
        
        Args:
            expression: The expression to sanitize
            
        Returns:
            Sanitized expression
        """
        # Remove any non-math characters
        sanitized = re.sub(r"[^0-9+\-*/().,%\s]", "", expression)
        
        # Replace % with * 0.01 for percentage calculations
        sanitized = sanitized.replace("%", "* 0.01")
        
        # Add math. prefix to common math functions
        for func in ["sin", "cos", "tan", "log", "exp", "sqrt", "floor", "ceil"]:
            sanitized = re.sub(
                rf"\b{func}\b", f"math.{func}", sanitized
            )
        
        return sanitized
