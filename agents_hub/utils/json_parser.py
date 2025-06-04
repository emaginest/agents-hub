"""
Robust JSON parsing utilities for the Agents Hub framework.

This module provides utilities for extracting and parsing JSON from mixed content,
which is common when working with LLM responses that may include explanatory text
before or after the actual JSON data.
"""

import json
import re
import logging
from typing import Dict, Any, Optional, List, Tuple, Union

logger = logging.getLogger(__name__)


class JSONParsingError(Exception):
    """Custom exception for JSON parsing errors."""

    def __init__(
        self, message: str, original_content: str, attempted_strategies: List[str]
    ):
        super().__init__(message)
        self.original_content = original_content
        self.attempted_strategies = attempted_strategies


class RobustJSONParser:
    """
    A robust JSON parser that can extract JSON from mixed content using multiple strategies.
    """

    def __init__(self):
        self.strategies = [
            self._extract_json_by_brackets,
            self._extract_json_by_regex,
            self._extract_json_by_code_blocks,
            self._extract_json_by_lines,
        ]

    def parse(
        self, content: str, expected_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parse JSON from mixed content using multiple strategies.

        Args:
            content: The content that may contain JSON
            expected_schema: Optional schema to validate against

        Returns:
            Parsed JSON data

        Raises:
            JSONParsingError: If all parsing strategies fail
        """
        if not content or not content.strip():
            raise JSONParsingError(
                "Empty or whitespace-only content provided", content, []
            )

        attempted_strategies = []

        for strategy in self.strategies:
            try:
                strategy_name = strategy.__name__
                attempted_strategies.append(strategy_name)

                logger.debug(
                    f"Attempting JSON extraction with strategy: {strategy_name}"
                )

                extracted_json = strategy(content)
                if extracted_json:
                    parsed_data = json.loads(extracted_json)

                    # Validate against schema if provided
                    if expected_schema:
                        try:
                            self._validate_schema(parsed_data, expected_schema)
                        except ValueError as schema_error:
                            logger.debug(
                                f"Strategy {strategy_name} failed schema validation: {schema_error}"
                            )
                            continue

                    logger.debug(
                        f"Successfully parsed JSON using strategy: {strategy_name}"
                    )
                    return parsed_data

            except json.JSONDecodeError as e:
                logger.debug(
                    f"Strategy {strategy_name} failed with JSONDecodeError: {e}"
                )
                continue
            except Exception as e:
                logger.debug(f"Strategy {strategy_name} failed with error: {e}")
                continue

        # If all strategies failed, raise a comprehensive error
        raise JSONParsingError(
            f"Failed to extract valid JSON using all available strategies: {attempted_strategies}",
            content,
            attempted_strategies,
        )

    def _extract_json_by_brackets(self, content: str) -> Optional[str]:
        """
        Extract JSON by finding balanced curly brackets.

        Args:
            content: Content to search

        Returns:
            Extracted JSON string or None
        """
        content = content.strip()

        # Find the first opening brace
        start_idx = content.find("{")
        if start_idx == -1:
            return None

        # Find the matching closing brace
        brace_count = 0
        bracket_count = 0
        in_string = False
        escape_next = False

        for i, char in enumerate(content[start_idx:], start_idx):
            if escape_next:
                escape_next = False
                continue

            if char == "\\":
                escape_next = True
                continue

            if char == '"' and not escape_next:
                in_string = not in_string
                continue

            if not in_string:
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        return content[start_idx : i + 1]
                elif char == "[":
                    bracket_count += 1
                elif char == "]":
                    bracket_count -= 1

        # If we reach here, brackets are not balanced
        return None

    def _extract_json_by_regex(self, content: str) -> Optional[str]:
        """
        Extract JSON using regex patterns.

        Args:
            content: Content to search

        Returns:
            Extracted JSON string or None
        """
        # Pattern to match JSON objects
        patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple nested objects
            r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}",  # More complex nesting
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                try:
                    # Test if it's valid JSON
                    json.loads(match)
                    return match
                except json.JSONDecodeError:
                    continue

        return None

    def _extract_json_by_code_blocks(self, content: str) -> Optional[str]:
        """
        Extract JSON from markdown code blocks.

        Args:
            content: Content to search

        Returns:
            Extracted JSON string or None
        """
        # Look for JSON in code blocks
        patterns = [
            r"```json\s*(.*?)\s*```",
            r"```\s*(.*?)\s*```",
            r"`(.*?)`",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                match = match.strip()
                if match.startswith("{") and match.endswith("}"):
                    try:
                        json.loads(match)
                        return match
                    except json.JSONDecodeError:
                        continue

        return None

    def _extract_json_by_lines(self, content: str) -> Optional[str]:
        """
        Extract JSON by analyzing lines and finding JSON-like content.

        Args:
            content: Content to search

        Returns:
            Extracted JSON string or None
        """
        lines = content.split("\n")
        json_lines = []
        in_json = False

        for line in lines:
            line = line.strip()

            # Start of JSON
            if line.startswith("{") and not in_json:
                in_json = True
                json_lines = [line]
            elif in_json:
                json_lines.append(line)
                # End of JSON
                if line.endswith("}"):
                    potential_json = "\n".join(json_lines)
                    try:
                        json.loads(potential_json)
                        return potential_json
                    except json.JSONDecodeError:
                        # Continue looking
                        pass

        return None

    def _validate_schema(
        self, data: Dict[str, Any], expected_schema: Dict[str, Any]
    ) -> None:
        """
        Validate parsed data against expected schema.

        Args:
            data: Parsed JSON data
            expected_schema: Expected schema structure

        Raises:
            ValueError: If validation fails
        """
        for key, expected_type in expected_schema.items():
            if key not in data:
                raise ValueError(f"Missing required key: {key}")

            if expected_type and not isinstance(data[key], expected_type):
                raise ValueError(
                    f"Key '{key}' should be of type {expected_type}, got {type(data[key])}"
                )


# Convenience function for simple use cases
def extract_json(
    content: str, expected_schema: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extract and parse JSON from mixed content.

    Args:
        content: Content that may contain JSON
        expected_schema: Optional schema to validate against

    Returns:
        Parsed JSON data

    Raises:
        JSONParsingError: If parsing fails
    """
    parser = RobustJSONParser()
    return parser.parse(content, expected_schema)
