"""
Tests for the intelligent agent selector.
"""

import pytest
from unittest.mock import Mock, MagicMock
from agents_hub.orchestration.agent_selector import AgentSelector


class TestAgentSelector:
    """Test cases for the AgentSelector class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create mock agents
        self.researcher_agent = Mock()
        self.researcher_agent.config.name = "researcher"
        self.researcher_agent.config.description = "Research assistant that finds and analyzes information"
        self.researcher_agent.config.system_prompt = "You are a researcher who finds accurate information"
        self.researcher_agent.tools = []

        self.writer_agent = Mock()
        self.writer_agent.config.name = "writer"
        self.writer_agent.config.description = "Writer and editor that creates content"
        self.writer_agent.config.system_prompt = "You are a skilled writer who creates engaging content"
        self.writer_agent.tools = []

        self.coder_agent = Mock()
        self.coder_agent.config.name = "coder"
        self.coder_agent.config.description = "Programmer that writes and debugs code"
        self.coder_agent.config.system_prompt = "You are an expert programmer who writes clean code"
        self.coder_agent.tools = []

        self.agents = {
            "researcher": self.researcher_agent,
            "writer": self.writer_agent,
            "coder": self.coder_agent,
        }

        self.selector = AgentSelector(self.agents)

    def test_initialization(self):
        """Test that AgentSelector initializes correctly."""
        assert len(self.selector.agents) == 3
        assert len(self.selector.agent_profiles) == 3
        assert "researcher" in self.selector.agent_profiles
        assert "writer" in self.selector.agent_profiles
        assert "coder" in self.selector.agent_profiles

    def test_extract_keywords(self):
        """Test keyword extraction from agent configuration."""
        keywords = self.selector._extract_keywords(self.researcher_agent)
        
        # Should include words from description and system prompt
        assert "research" in keywords or "researcher" in keywords
        assert "information" in keywords
        assert "accurate" in keywords
        
        # Should filter out short words and common words
        assert "and" not in keywords
        assert "the" not in keywords

    def test_extract_capabilities(self):
        """Test capability extraction from agent configuration."""
        capabilities = self.selector._extract_capabilities(self.coder_agent)
        
        # Should include capability-related words
        assert any("program" in cap or "code" in cap for cap in capabilities)

    def test_tokenize_text(self):
        """Test text tokenization."""
        text = "This is a test with punctuation! And numbers 123."
        tokens = self.selector._tokenize_text(text)
        
        # Should include meaningful words
        assert "test" in tokens
        assert "punctuation" in tokens
        
        # Should exclude short words and numbers
        assert "is" not in tokens  # Too short
        assert "123" not in tokens  # Number

    def test_select_best_agent_research_task(self):
        """Test agent selection for a research-related task."""
        task = "Research the latest developments in artificial intelligence"
        selected_agent = self.selector.select_best_agent(task)
        
        # Should select the researcher agent
        assert selected_agent == "researcher"

    def test_select_best_agent_writing_task(self):
        """Test agent selection for a writing-related task."""
        task = "Write a compelling blog post about machine learning"
        selected_agent = self.selector.select_best_agent(task)
        
        # Should select the writer agent
        assert selected_agent == "writer"

    def test_select_best_agent_coding_task(self):
        """Test agent selection for a coding-related task."""
        task = "Write a Python function to calculate fibonacci numbers"
        selected_agent = self.selector.select_best_agent(task)
        
        # Should select the coder agent
        assert selected_agent == "coder"

    def test_select_best_agent_programming_task(self):
        """Test agent selection for a programming-related task."""
        task = "Debug this JavaScript code and fix the errors"
        selected_agent = self.selector.select_best_agent(task)
        
        # Should select the coder agent
        assert selected_agent == "coder"

    def test_select_best_agent_ambiguous_task(self):
        """Test agent selection for an ambiguous task."""
        task = "Help me with my project"
        selected_agent = self.selector.select_best_agent(task)
        
        # Should select some agent (any is valid for ambiguous tasks)
        assert selected_agent in ["researcher", "writer", "coder"]

    def test_select_best_agent_empty_agents(self):
        """Test that selection fails with no agents."""
        empty_selector = AgentSelector({})
        
        with pytest.raises(ValueError, match="No agents available"):
            empty_selector.select_best_agent("any task")

    def test_calculate_keyword_score(self):
        """Test keyword score calculation."""
        task_tokens = ["research", "artificial", "intelligence"]
        agent_keywords = ["research", "information", "analysis"]
        
        score = self.selector._calculate_keyword_score(task_tokens, agent_keywords)
        
        # Should be 1/3 since only "research" matches
        assert score == pytest.approx(1/3, rel=1e-2)

    def test_calculate_keyword_score_no_keywords(self):
        """Test keyword score with no agent keywords."""
        task_tokens = ["research", "artificial", "intelligence"]
        agent_keywords = []
        
        score = self.selector._calculate_keyword_score(task_tokens, agent_keywords)
        assert score == 0.0

    def test_calculate_capability_score(self):
        """Test capability score calculation."""
        task = "research and analyze data"
        capabilities = ["research", "analyze", "write"]
        
        score = self.selector._calculate_capability_score(task, capabilities)
        
        # Should be 2/3 since "research" and "analyze" match
        assert score == pytest.approx(2/3, rel=1e-2)

    def test_calculate_description_score(self):
        """Test description similarity score calculation."""
        task = "research artificial intelligence"
        description = "research assistant that finds information"
        
        score = self.selector._calculate_description_score(task, description)
        
        # Should be > 0 due to "research" similarity
        assert score > 0

    def test_calculate_name_score_exact_match(self):
        """Test name score with exact match."""
        task = "use the researcher agent"
        agent_name = "researcher"
        
        score = self.selector._calculate_name_score(task, agent_name)
        assert score == 1.0

    def test_calculate_name_score_partial_match(self):
        """Test name score with partial match."""
        task = "need some research help"
        agent_name = "researcher"
        
        score = self.selector._calculate_name_score(task, agent_name)
        # Should be > 0 but < 1 due to partial match
        assert 0 < score < 1

    def test_calculate_name_score_no_match(self):
        """Test name score with no match."""
        task = "write some code"
        agent_name = "researcher"
        
        score = self.selector._calculate_name_score(task, agent_name)
        assert score == 0.0

    def test_get_ranked_agents(self):
        """Test getting all agents ranked by suitability."""
        task = "research machine learning algorithms"
        ranked_agents = self.selector.get_ranked_agents(task)
        
        # Should return all agents with scores
        assert len(ranked_agents) == 3
        
        # Should be sorted by score descending
        scores = [score for _, score in ranked_agents]
        assert scores == sorted(scores, reverse=True)
        
        # Researcher should likely be first for this task
        assert ranked_agents[0][0] == "researcher"

    def test_get_ranked_agents_empty(self):
        """Test ranked agents with no agents."""
        empty_selector = AgentSelector({})
        ranked_agents = empty_selector.get_ranked_agents("any task")
        
        assert ranked_agents == []

    def test_agent_score_calculation_comprehensive(self):
        """Test comprehensive agent score calculation."""
        task = "research and write about quantum computing"
        task_tokens = self.selector._tokenize_text(task)
        profile = self.selector.agent_profiles["researcher"]
        
        score = self.selector._calculate_agent_score(task, task_tokens, profile, None)
        
        # Score should be between 0 and 1
        assert 0 <= score <= 1

    def test_build_agent_profiles(self):
        """Test that agent profiles are built correctly."""
        profile = self.selector.agent_profiles["researcher"]
        
        assert profile["name"] == "researcher"
        assert "research" in profile["description"].lower()
        assert len(profile["keywords"]) > 0
        assert isinstance(profile["capabilities"], list)

    def test_stop_words_filtering(self):
        """Test that stop words are properly filtered."""
        stop_words = self.selector._get_stop_words()
        
        # Common stop words should be included
        assert "the" in stop_words
        assert "and" in stop_words
        assert "you" in stop_words

    def test_select_with_context(self):
        """Test agent selection with additional context."""
        task = "help with my project"
        context = {"domain": "research", "priority": "high"}
        
        selected_agent = self.selector.select_best_agent(task, context)
        
        # Should still select a valid agent
        assert selected_agent in ["researcher", "writer", "coder"]
