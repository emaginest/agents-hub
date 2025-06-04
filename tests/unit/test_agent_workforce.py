"""
Tests for the improved AgentWorkforce orchestration system.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from agents_hub.orchestration.router import AgentWorkforce
from agents_hub.utils.json_parser import JSONParsingError


class TestAgentWorkforce:
    """Test cases for the AgentWorkforce class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create mock agents
        self.researcher_agent = Mock()
        self.researcher_agent.config.name = "researcher"
        self.researcher_agent.config.description = "Research assistant"
        self.researcher_agent.config.system_prompt = "You are a researcher"
        self.researcher_agent.run = AsyncMock(return_value="Research result")
        self.researcher_agent.tools = []

        self.writer_agent = Mock()
        self.writer_agent.config.name = "writer"
        self.writer_agent.config.description = "Content writer"
        self.writer_agent.config.system_prompt = "You are a writer"
        self.writer_agent.run = AsyncMock(return_value="Writing result")
        self.writer_agent.tools = []

        self.orchestrator_agent = Mock()
        self.orchestrator_agent.config.name = "orchestrator"
        self.orchestrator_agent.config.description = "Task orchestrator"
        self.orchestrator_agent.config.system_prompt = "You are an orchestrator"
        self.orchestrator_agent.run = AsyncMock()
        self.orchestrator_agent.tools = []

        self.agents = [self.researcher_agent, self.writer_agent]

    def test_initialization_without_orchestrator(self):
        """Test AgentWorkforce initialization without orchestrator."""
        workforce = AgentWorkforce(agents=self.agents)

        assert len(workforce.agents) == 2
        assert "researcher" in workforce.agents
        assert "writer" in workforce.agents
        assert workforce.orchestrator is None
        assert workforce.agent_selector is not None

    def test_initialization_with_orchestrator(self):
        """Test AgentWorkforce initialization with orchestrator."""
        workforce = AgentWorkforce(
            agents=self.agents, orchestrator_agent=self.orchestrator_agent
        )

        assert len(workforce.agents) == 2
        assert workforce.orchestrator == self.orchestrator_agent
        assert workforce.agent_selector is not None

    @pytest.mark.asyncio
    async def test_execute_with_specific_agent(self):
        """Test task execution with a specific agent name."""
        workforce = AgentWorkforce(agents=self.agents)

        result = await workforce.execute(task="Test task", agent_name="researcher")

        assert result["agent"] == "researcher"
        assert result["result"] == "Research result"
        assert result["subtasks"] == []
        self.researcher_agent.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_without_orchestrator_uses_intelligent_selection(self):
        """Test that execution without orchestrator uses intelligent agent selection."""
        workforce = AgentWorkforce(agents=self.agents)

        with patch.object(
            workforce.agent_selector, "select_best_agent", return_value="writer"
        ):
            result = await workforce.execute(task="Write a blog post")

            assert result["agent"] == "writer"
            assert result["result"] == "Writing result"
            assert result["selection_method"] == "intelligent_fallback"

    @pytest.mark.asyncio
    async def test_execute_intelligent_selection_fallback(self):
        """Test fallback to first agent when intelligent selection fails."""
        workforce = AgentWorkforce(agents=self.agents)

        with patch.object(
            workforce.agent_selector,
            "select_best_agent",
            side_effect=Exception("Selection failed"),
        ):
            result = await workforce.execute(task="Test task")

            assert result["agent"] == "researcher"  # First agent
            assert result["selection_method"] == "first_agent_fallback"
            assert "Selection failed" in result["fallback_reason"]

    @pytest.mark.asyncio
    async def test_orchestrated_execution_success(self):
        """Test successful orchestrated execution."""
        self.orchestrator_agent.run.return_value = """
        {
            "subtasks": [
                {"description": "Research topic", "agent": "researcher", "order": 1},
                {"description": "Write summary", "agent": "writer", "order": 2}
            ]
        }
        """

        workforce = AgentWorkforce(
            agents=self.agents, orchestrator_agent=self.orchestrator_agent
        )

        result = await workforce.execute(task="Research and write about AI")

        assert result["agent"] == "orchestrator"
        assert len(result["subtasks"]) == 2
        assert result["subtasks"][0]["agent"] == "researcher"
        assert result["subtasks"][1]["agent"] == "writer"

    @pytest.mark.asyncio
    async def test_orchestrated_execution_json_parsing_failure(self):
        """Test orchestrated execution with JSON parsing failure."""
        self.orchestrator_agent.run.return_value = "This is not valid JSON at all"

        workforce = AgentWorkforce(
            agents=self.agents, orchestrator_agent=self.orchestrator_agent
        )

        with patch.object(
            workforce.agent_selector, "select_best_agent", return_value="researcher"
        ):
            result = await workforce.execute(task="Test task")

            assert result["selection_method"] == "intelligent_fallback"
            assert "JSON parsing failed" in result["fallback_reason"]

    @pytest.mark.asyncio
    async def test_orchestrated_execution_mixed_content_json(self):
        """Test orchestrated execution with JSON in mixed content."""
        self.orchestrator_agent.run.return_value = """
        I'll break this down into subtasks:
        
        {
            "subtasks": [
                {"description": "Research topic", "agent": "researcher", "order": 1}
            ]
        }
        
        This should work well for the task.
        """

        workforce = AgentWorkforce(
            agents=self.agents, orchestrator_agent=self.orchestrator_agent
        )

        result = await workforce.execute(task="Research AI")

        assert result["agent"] == "orchestrator"
        assert len(result["subtasks"]) == 1
        assert result["subtasks"][0]["agent"] == "researcher"

    @pytest.mark.asyncio
    async def test_orchestrated_execution_unknown_agent_fallback(self):
        """Test orchestrated execution with unknown agent uses intelligent selection."""
        self.orchestrator_agent.run.return_value = """
        {
            "subtasks": [
                {"description": "Test task", "agent": "unknown_agent", "order": 1}
            ]
        }
        """

        workforce = AgentWorkforce(
            agents=self.agents, orchestrator_agent=self.orchestrator_agent
        )

        with patch.object(
            workforce.agent_selector, "select_best_agent", return_value="writer"
        ):
            result = await workforce.execute(task="Test task")

            # Should use intelligent selection for unknown agent
            assert len(result["subtasks"]) == 1
            assert result["subtasks"][0]["agent"] == "writer"
            assert result["subtasks"][0]["selection_method"] == "intelligent_fallback"

    @pytest.mark.asyncio
    async def test_orchestrated_execution_unknown_agent_final_fallback(self):
        """Test final fallback when both orchestration and intelligent selection fail."""
        self.orchestrator_agent.run.return_value = """
        {
            "subtasks": [
                {"description": "Test task", "agent": "unknown_agent", "order": 1}
            ]
        }
        """

        workforce = AgentWorkforce(
            agents=self.agents, orchestrator_agent=self.orchestrator_agent
        )

        with patch.object(
            workforce.agent_selector,
            "select_best_agent",
            side_effect=Exception("Selection failed"),
        ):
            result = await workforce.execute(task="Test task")

            # Should use first agent as final fallback
            assert len(result["subtasks"]) == 1
            assert result["subtasks"][0]["agent"] == "researcher"  # First agent
            assert result["subtasks"][0]["selection_method"] == "first_agent_fallback"

    @pytest.mark.asyncio
    async def test_intelligent_fallback_execution(self):
        """Test the intelligent fallback execution method."""
        workforce = AgentWorkforce(agents=self.agents)

        with patch.object(
            workforce.agent_selector, "select_best_agent", return_value="writer"
        ):
            result = await workforce._intelligent_fallback_execution(
                task="Write content", context={}, error_reason="Test error"
            )

            assert result["agent"] == "writer"
            assert result["selection_method"] == "intelligent_fallback"
            assert result["fallback_reason"] == "Test error"

    @pytest.mark.asyncio
    async def test_intelligent_fallback_execution_fails(self):
        """Test intelligent fallback execution when selection fails."""
        workforce = AgentWorkforce(agents=self.agents)

        with patch.object(
            workforce.agent_selector,
            "select_best_agent",
            side_effect=Exception("Selection error"),
        ):
            result = await workforce._intelligent_fallback_execution(
                task="Test task", context={}, error_reason="Original error"
            )

            assert result["agent"] == "researcher"  # First agent
            assert result["selection_method"] == "first_agent_fallback"
            assert "Original error" in result["fallback_reason"]
            assert "Selection error" in result["fallback_reason"]

    def test_add_agent(self):
        """Test adding an agent to the workforce."""
        workforce = AgentWorkforce(agents=self.agents)

        new_agent = Mock()
        new_agent.config.name = "coder"
        new_agent.config.description = "Code writer"
        new_agent.config.system_prompt = "You are a coder"
        new_agent.tools = []

        workforce.add_agent(new_agent)

        assert "coder" in workforce.agents
        assert len(workforce.agents) == 3
        # Agent selector should be refreshed
        assert "coder" in workforce.agent_selector.agents

    def test_remove_agent(self):
        """Test removing an agent from the workforce."""
        workforce = AgentWorkforce(agents=self.agents)

        workforce.remove_agent("writer")

        assert "writer" not in workforce.agents
        assert len(workforce.agents) == 1
        # Agent selector should be refreshed
        assert "writer" not in workforce.agent_selector.agents

    def test_get_agent(self):
        """Test getting an agent by name."""
        workforce = AgentWorkforce(agents=self.agents)

        agent = workforce.get_agent("researcher")
        assert agent == self.researcher_agent

        agent = workforce.get_agent("nonexistent")
        assert agent is None

    @pytest.mark.asyncio
    async def test_execute_with_invalid_agent_name(self):
        """Test execution with invalid agent name falls back to intelligent selection."""
        workforce = AgentWorkforce(agents=self.agents)

        with patch.object(
            workforce.agent_selector, "select_best_agent", return_value="writer"
        ):
            result = await workforce.execute(
                task="Test task", agent_name="nonexistent_agent"
            )

            # Should fall back to intelligent selection
            assert result["agent"] == "writer"
            assert result["selection_method"] == "intelligent_fallback"
