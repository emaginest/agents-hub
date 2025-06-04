"""
Tests for the robust JSON parser utilities.
"""

import pytest
from agents_hub.utils.json_parser import (
    RobustJSONParser,
    extract_json,
    JSONParsingError,
)


class TestRobustJSONParser:
    """Test cases for the RobustJSONParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = RobustJSONParser()

    def test_parse_clean_json(self):
        """Test parsing clean JSON without any extra content."""
        json_content = (
            '{"subtasks": [{"description": "test", "agent": "researcher", "order": 1}]}'
        )
        result = self.parser.parse(json_content)

        assert result == {
            "subtasks": [{"description": "test", "agent": "researcher", "order": 1}]
        }

    def test_parse_json_with_explanation_before(self):
        """Test parsing JSON with explanatory text before."""
        content = """
        I'll break down this task into subtasks:
        
        {"subtasks": [{"description": "research topic", "agent": "researcher", "order": 1}]}
        """
        result = self.parser.parse(content)

        assert result == {
            "subtasks": [
                {"description": "research topic", "agent": "researcher", "order": 1}
            ]
        }

    def test_parse_json_with_explanation_after(self):
        """Test parsing JSON with explanatory text after."""
        content = """
        {"subtasks": [{"description": "analyze data", "agent": "analyst", "order": 1}]}
        
        This plan will help accomplish the task efficiently.
        """
        result = self.parser.parse(content)

        assert result == {
            "subtasks": [
                {"description": "analyze data", "agent": "analyst", "order": 1}
            ]
        }

    def test_parse_json_in_code_blocks(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        content = """
        Here's the plan:
        
        ```json
        {"subtasks": [{"description": "write code", "agent": "coder", "order": 1}]}
        ```
        """
        result = self.parser.parse(content)

        assert result == {
            "subtasks": [{"description": "write code", "agent": "coder", "order": 1}]
        }

    def test_parse_json_in_generic_code_blocks(self):
        """Test parsing JSON in generic code blocks."""
        content = """
        ```
        {"subtasks": [{"description": "test feature", "agent": "tester", "order": 1}]}
        ```
        """
        result = self.parser.parse(content)

        assert result == {
            "subtasks": [{"description": "test feature", "agent": "tester", "order": 1}]
        }

    def test_parse_multiline_json(self):
        """Test parsing multiline JSON."""
        content = """
        {
            "subtasks": [
                {
                    "description": "research quantum computing",
                    "agent": "researcher",
                    "order": 1
                },
                {
                    "description": "write summary",
                    "agent": "writer",
                    "order": 2
                }
            ]
        }
        """
        result = self.parser.parse(content)

        assert len(result["subtasks"]) == 2
        assert result["subtasks"][0]["description"] == "research quantum computing"
        assert result["subtasks"][1]["description"] == "write summary"

    def test_parse_nested_json(self):
        """Test parsing nested JSON structures."""
        content = """
        {
            "subtasks": [
                {
                    "description": "complex task",
                    "agent": "researcher",
                    "order": 1,
                    "metadata": {
                        "priority": "high",
                        "tags": ["urgent", "research"]
                    }
                }
            ]
        }
        """
        result = self.parser.parse(content)

        assert result["subtasks"][0]["metadata"]["priority"] == "high"
        assert "urgent" in result["subtasks"][0]["metadata"]["tags"]

    def test_parse_with_schema_validation(self):
        """Test parsing with schema validation."""
        content = (
            '{"subtasks": [{"description": "test", "agent": "researcher", "order": 1}]}'
        )
        expected_schema = {"subtasks": list}

        result = self.parser.parse(content, expected_schema)
        assert isinstance(result["subtasks"], list)

    def test_parse_fails_schema_validation(self):
        """Test that parsing fails when schema validation fails."""
        content = '{"wrong_key": "value"}'
        expected_schema = {"subtasks": list}

        with pytest.raises(JSONParsingError, match="Failed to extract valid JSON"):
            self.parser.parse(content, expected_schema)

    def test_parse_empty_content(self):
        """Test parsing empty content raises appropriate error."""
        with pytest.raises(JSONParsingError, match="Empty or whitespace-only content"):
            self.parser.parse("")

    def test_parse_no_json_content(self):
        """Test parsing content with no JSON raises appropriate error."""
        content = "This is just plain text with no JSON at all."

        with pytest.raises(JSONParsingError) as exc_info:
            self.parser.parse(content)

        assert "Failed to extract valid JSON" in str(exc_info.value)
        assert exc_info.value.original_content == content
        assert len(exc_info.value.attempted_strategies) > 0

    def test_parse_malformed_json(self):
        """Test parsing malformed JSON that has no valid JSON objects."""
        content = '{"broken": json, "missing": quotes}'  # Completely malformed

        with pytest.raises(JSONParsingError):
            self.parser.parse(content)

    def test_parse_incomplete_json_finds_inner_object(self):
        """Test that parser can find valid inner objects in incomplete JSON."""
        content = '{"subtasks": [{"description": "test", "agent": "researcher", "order": 1}'  # Missing closing brackets
        result = self.parser.parse(content)

        # Should find the inner valid object
        assert result == {"description": "test", "agent": "researcher", "order": 1}

    def test_extract_json_by_brackets(self):
        """Test the bracket-based extraction strategy."""
        content = 'Some text {"key": "value"} more text'
        result = self.parser._extract_json_by_brackets(content)
        assert result == '{"key": "value"}'

    def test_extract_json_by_brackets_nested(self):
        """Test bracket extraction with nested objects."""
        content = 'Text {"outer": {"inner": "value"}} more'
        result = self.parser._extract_json_by_brackets(content)
        assert result == '{"outer": {"inner": "value"}}'

    def test_extract_json_by_brackets_no_json(self):
        """Test bracket extraction when no JSON present."""
        content = "No JSON here at all"
        result = self.parser._extract_json_by_brackets(content)
        assert result is None

    def test_convenience_function(self):
        """Test the convenience extract_json function."""
        content = 'Here is the JSON: {"test": "value"}'
        result = extract_json(content)
        assert result == {"test": "value"}

    def test_multiple_json_objects_first_valid(self):
        """Test that the first valid JSON object is returned."""
        content = """
        Invalid: {"broken": json}
        Valid: {"subtasks": [{"description": "test", "agent": "researcher", "order": 1}]}
        """
        result = self.parser.parse(content)
        assert result == {
            "subtasks": [{"description": "test", "agent": "researcher", "order": 1}]
        }


class TestJSONParsingError:
    """Test cases for JSONParsingError exception."""

    def test_json_parsing_error_attributes(self):
        """Test that JSONParsingError stores the expected attributes."""
        original_content = "invalid content"
        attempted_strategies = ["strategy1", "strategy2"]

        error = JSONParsingError("Test error", original_content, attempted_strategies)

        assert str(error) == "Test error"
        assert error.original_content == original_content
        assert error.attempted_strategies == attempted_strategies
