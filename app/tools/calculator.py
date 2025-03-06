import math
from typing import Dict, Any
import re


class Calculator:
    """A tool for performing mathematical calculations."""

    def calculate(self, expression: str) -> float:
        """
        Calculate the result of a mathematical expression.

        Args:
            expression: A string containing a mathematical expression

        Returns:
            The calculated result

        Raises:
            ValueError: If the expression is invalid or contains unsupported operations
        """
        # Remove all whitespace
        expression = "".join(expression.split())

        # Basic validation
        if not re.match(r"^[\d\+\-\*\/\(\)\.\s]*$", expression):
            raise ValueError("Invalid characters in expression")

        try:
            # Use eval with a restricted local dict for basic arithmetic
            local_dict = {"__builtins__": None}
            # Add safe math functions
            local_dict.update(
                {
                    "abs": abs,
                    "round": round,
                    "max": max,
                    "min": min,
                    "pow": pow,
                    "sqrt": math.sqrt,
                }
            )

            result = eval(expression, {"__builtins__": {}}, local_dict)

            if not isinstance(result, (int, float)):
                raise ValueError("Invalid result type")

            return float(result)

        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the calculator tool with the provided input.

        Args:
            input_data: Dictionary containing:
                - expression: The mathematical expression to evaluate

        Returns:
            Dictionary containing:
                - result: The calculated result
        """
        if "expression" not in input_data:
            raise ValueError("Missing 'expression' in input")

        expression = input_data["expression"]
        result = self.calculate(expression)

        return {"result": result}


# Create a global instance
calculator = Calculator()
