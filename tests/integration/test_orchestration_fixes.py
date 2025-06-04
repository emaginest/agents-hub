"""
Integration tests for the AgentWorkforce orchestration fixes.

These tests demonstrate that the critical bugs have been fixed:
1. Robust JSON parsing from mixed content
2. Intelligent fallback logic instead of defaulting to first agent
3. Proper error handling and logging
"""

import pytest
from unittest.mock import Mock, AsyncMock
from agents_hub.orchestration.router import AgentWorkforce
from agents_hub.utils.json_parser import extract_json, JSONParsingError


class TestOrchestrationFixes:
    """Integration tests for orchestration bug fixes."""

    def setup_method(self):
        """Set up test fixtures with realistic agent configurations."""
        # Create specialized agents with realistic configurations
        self.research_agent = Mock()
        self.research_agent.config.name = "research_specialist"
        self.research_agent.config.description = (
            "Expert researcher who finds and analyzes information from various sources"
        )
        self.research_agent.config.system_prompt = (
            "You are a research specialist who excels at finding accurate information"
        )
        self.research_agent.run = AsyncMock(
            return_value="Comprehensive research findings on the topic"
        )
        self.research_agent.tools = []

        self.writing_agent = Mock()
        self.writing_agent.config.name = "content_writer"
        self.writing_agent.config.description = (
            "Professional writer who creates engaging and clear content"
        )
        self.writing_agent.config.system_prompt = (
            "You are a skilled content writer who creates compelling narratives"
        )
        self.writing_agent.run = AsyncMock(
            return_value="Well-written article with engaging content"
        )
        self.writing_agent.tools = []

        self.coding_agent = Mock()
        self.coding_agent.config.name = "software_developer"
        self.coding_agent.config.description = (
            "Expert programmer who writes clean, efficient code"
        )
        self.coding_agent.config.system_prompt = (
            "You are a software developer who writes high-quality code"
        )
        self.coding_agent.run = AsyncMock(
            return_value="Clean, well-documented code solution"
        )
        self.coding_agent.tools = []

        self.orchestrator = Mock()
        self.orchestrator.config.name = "task_orchestrator"
        self.orchestrator.config.description = (
            "Coordinates tasks between specialized agents"
        )
        self.orchestrator.config.system_prompt = "You coordinate tasks between agents"
        self.orchestrator.run = AsyncMock()
        self.orchestrator.tools = []

        self.agents = [self.research_agent, self.writing_agent, self.coding_agent]

    @pytest.mark.asyncio
    async def test_fix_json_parsing_with_explanatory_text(self):
        """Test that JSON parsing works with explanatory text (Bug Fix #1)."""
        # Simulate LLM response with explanation before JSON
        self.orchestrator.run.return_value = """
        I'll break down this task into subtasks for the specialized agents:

        {
            "subtasks": [
                {
                    "description": "Research the latest trends in artificial intelligence",
                    "agent": "research_specialist",
                    "order": 1
                },
                {
                    "description": "Write an engaging article about AI trends",
                    "agent": "content_writer",
                    "order": 2
                }
            ]
        }

        This plan will ensure comprehensive coverage of the topic.
        """

        workforce = AgentWorkforce(
            agents=self.agents, orchestrator_agent=self.orchestrator
        )

        result = await workforce.execute("Create an article about AI trends")

        # Should successfully parse JSON and execute subtasks
        assert result["agent"] == "task_orchestrator"
        assert len(result["subtasks"]) == 2
        assert result["subtasks"][0]["agent"] == "research_specialist"
        assert result["subtasks"][1]["agent"] == "content_writer"

    @pytest.mark.asyncio
    async def test_fix_json_parsing_in_code_blocks(self):
        """Test that JSON parsing works with markdown code blocks (Bug Fix #1)."""
        # Simulate LLM response with JSON in code blocks
        self.orchestrator.run.return_value = """
        Here's my orchestration plan:

        ```json
        {
            "subtasks": [
                {
                    "description": "Write a Python function for data processing",
                    "agent": "software_developer",
                    "order": 1
                }
            ]
        }
        ```

        This should handle the coding task efficiently.
        """

        workforce = AgentWorkforce(
            agents=self.agents, orchestrator_agent=self.orchestrator
        )

        result = await workforce.execute("Create a data processing function")

        # Should successfully parse JSON from code block
        assert result["agent"] == "task_orchestrator"
        assert len(result["subtasks"]) == 1
        assert result["subtasks"][0]["agent"] == "software_developer"

    @pytest.mark.asyncio
    async def test_fix_intelligent_fallback_for_research_task(self):
        """Test intelligent fallback selects research agent for research tasks (Bug Fix #2)."""
        # Simulate complete JSON parsing failure
        self.orchestrator.run.return_value = (
            "This is completely invalid JSON with no structure at all!"
        )

        workforce = AgentWorkforce(
            agents=self.agents, orchestrator_agent=self.orchestrator
        )

        result = await workforce.execute(
            "Research the impact of climate change on agriculture"
        )

        # Should use intelligent fallback and select research agent (not first agent)
        assert result["selection_method"] == "intelligent_fallback"
        assert (
            result["agent"] == "research_specialist"
        )  # Should select based on task content
        assert "JSON parsing failed" in result["fallback_reason"]

    @pytest.mark.asyncio
    async def test_fix_intelligent_fallback_for_writing_task(self):
        """Test intelligent fallback selects writing agent for writing tasks (Bug Fix #2)."""
        # Simulate JSON parsing failure
        self.orchestrator.run.return_value = "Invalid response: {broken json structure"

        workforce = AgentWorkforce(
            agents=self.agents, orchestrator_agent=self.orchestrator
        )

        result = await workforce.execute(
            "Write a compelling blog post about sustainable technology"
        )

        # Should use intelligent fallback and select writing agent
        assert result["selection_method"] == "intelligent_fallback"
        assert (
            result["agent"] == "content_writer"
        )  # Should select based on task content
        assert "JSON parsing failed" in result["fallback_reason"]

    @pytest.mark.asyncio
    async def test_fix_intelligent_fallback_for_coding_task(self):
        """Test intelligent fallback selects coding agent for coding tasks (Bug Fix #2)."""
        # Simulate JSON parsing failure
        self.orchestrator.run.return_value = "Error: Cannot parse this as JSON"

        workforce = AgentWorkforce(
            agents=self.agents, orchestrator_agent=self.orchestrator
        )

        result = await workforce.execute(
            "Implement a REST API using FastAPI with authentication"
        )

        # Should use intelligent fallback and select coding agent
        assert result["selection_method"] == "intelligent_fallback"
        assert (
            result["agent"] == "software_developer"
        )  # Should select based on task content
        assert "JSON parsing failed" in result["fallback_reason"]

    @pytest.mark.asyncio
    async def test_fix_unknown_agent_intelligent_selection(self):
        """Test intelligent selection when orchestrator references unknown agent (Bug Fix #3)."""
        # Simulate orchestrator referencing non-existent agent
        self.orchestrator.run.return_value = """
        {
            "subtasks": [
                {
                    "description": "Research quantum computing applications",
                    "agent": "quantum_specialist",
                    "order": 1
                },
                {
                    "description": "Write technical documentation",
                    "agent": "content_writer",
                    "order": 2
                }
            ]
        }
        """

        workforce = AgentWorkforce(
            agents=self.agents, orchestrator_agent=self.orchestrator
        )

        result = await workforce.execute("Create documentation about quantum computing")

        # Should handle unknown agent intelligently
        assert len(result["subtasks"]) == 2

        # First subtask should use intelligent selection (quantum_specialist doesn't exist)
        first_subtask = result["subtasks"][0]
        assert first_subtask["selection_method"] == "intelligent_fallback"
        assert (
            first_subtask["agent"] == "research_specialist"
        )  # Should select research agent for research task
        assert first_subtask["original_agent"] == "quantum_specialist"

        # Second subtask should work normally
        second_subtask = result["subtasks"][1]
        assert second_subtask["agent"] == "content_writer"

    @pytest.mark.asyncio
    async def test_fix_comprehensive_error_handling(self):
        """Test comprehensive error handling and logging (Bug Fix #4)."""
        # Simulate multiple failure modes
        self.orchestrator.run.return_value = (
            "Completely malformed response with no JSON"
        )

        workforce = AgentWorkforce(
            agents=self.agents, orchestrator_agent=self.orchestrator
        )

        result = await workforce.execute(
            "Complex multi-step task requiring coordination"
        )

        # Should provide detailed error information
        assert "selection_method" in result
        assert "fallback_reason" in result
        assert result["selection_method"] in [
            "intelligent_fallback",
            "first_agent_fallback",
        ]
        assert "JSON parsing failed" in result["fallback_reason"]

    @pytest.mark.asyncio
    async def test_fix_no_orchestrator_intelligent_selection(self):
        """Test intelligent selection when no orchestrator is provided."""
        # Create workforce without orchestrator
        workforce = AgentWorkforce(agents=self.agents)

        # Test different types of tasks
        research_result = await workforce.execute(
            "Analyze market trends in renewable energy"
        )
        writing_result = await workforce.execute(
            "Create a marketing copy for a new product"
        )
        coding_result = await workforce.execute("Build a web scraper using Python")

        # Should select appropriate agents based on task content
        assert research_result["agent"] == "research_specialist"
        assert research_result["selection_method"] == "intelligent_fallback"

        assert writing_result["agent"] == "content_writer"
        assert writing_result["selection_method"] == "intelligent_fallback"

        assert coding_result["agent"] == "software_developer"
        assert coding_result["selection_method"] == "intelligent_fallback"

    def test_json_parser_robustness(self):
        """Test the robust JSON parser handles various edge cases."""
        # Test various problematic formats that would break naive parsing
        test_cases = [
            # JSON with explanation before
            'Here is the plan: {"subtasks": [{"description": "test", "agent": "researcher", "order": 1}]}',
            # JSON with explanation after
            '{"subtasks": [{"description": "test", "agent": "researcher", "order": 1}]} This should work.',
            # JSON in code blocks
            '```json\n{"subtasks": [{"description": "test", "agent": "researcher", "order": 1}]}\n```',
            # Multiline JSON with extra text
            """
            I'll create this plan:
            {
                "subtasks": [
                    {
                        "description": "test task",
                        "agent": "researcher",
                        "order": 1
                    }
                ]
            }
            Hope this helps!
            """,
        ]

        for test_content in test_cases:
            result = extract_json(test_content)
            assert "subtasks" in result
            assert len(result["subtasks"]) == 1
            assert result["subtasks"][0]["description"] in ["test", "test task"]
            assert result["subtasks"][0]["agent"] == "researcher"

    def test_json_parser_failure_cases(self):
        """Test that JSON parser properly fails on invalid content."""
        invalid_cases = [
            "",  # Empty content
            "   ",  # Whitespace only
            "This is just plain text with no JSON",  # No JSON
            "Almost JSON but not quite: {broken",  # Malformed
        ]

        for invalid_content in invalid_cases:
            with pytest.raises(JSONParsingError):
                extract_json(invalid_content)

    @pytest.mark.asyncio
    async def test_end_to_end_orchestration_success(self):
        """Test complete end-to-end orchestration with all fixes working."""
        # Simulate realistic orchestrator response with mixed content
        self.orchestrator.run.side_effect = [
            # First call: orchestration plan
            """
            I'll coordinate this complex task across multiple agents:

            {
                "subtasks": [
                    {
                        "description": "Research current AI safety practices and regulations",
                        "agent": "research_specialist",
                        "order": 1
                    },
                    {
                        "description": "Develop a Python script for AI model evaluation",
                        "agent": "software_developer",
                        "order": 2
                    },
                    {
                        "description": "Write comprehensive documentation for the evaluation framework",
                        "agent": "content_writer",
                        "order": 3
                    }
                ]
            }

            This approach ensures thorough coverage of both technical and regulatory aspects.
            """,
            # Second call: summary generation
            "Comprehensive AI safety evaluation framework completed with research, implementation, and documentation.",
        ]

        workforce = AgentWorkforce(
            agents=self.agents, orchestrator_agent=self.orchestrator
        )

        result = await workforce.execute(
            "Create a comprehensive AI safety evaluation framework"
        )

        # Verify successful orchestration
        assert result["agent"] == "task_orchestrator"
        assert len(result["subtasks"]) == 3

        # Verify correct agent assignment
        assert result["subtasks"][0]["agent"] == "research_specialist"
        assert result["subtasks"][1]["agent"] == "software_developer"
        assert result["subtasks"][2]["agent"] == "content_writer"

        # Verify all agents were called
        self.research_agent.run.assert_called_once()
        self.coding_agent.run.assert_called_once()
        self.writing_agent.run.assert_called_once()

        # Verify orchestrator was called twice (plan + summary)
        assert self.orchestrator.run.call_count == 2
